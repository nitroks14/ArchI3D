"""
Deux mesures INDEPENDANTES et JAMAIS FUSIONNEES, calculees separement pour le rapport thermique :

1. `compute_structural_inertia_class` - classe d'inertie thermique simplifiee a 3 niveaux
   (leger/moyen/lourd), inspiree de l'approche RE2020 sans en reprendre la methode complete
   (5 classes normees Th-I, Cm en J/m2.K...). Derive de la masse surfacique approximative des
   materiaux/typologies des parois exposees cote interieur (murs exterieurs, planchers, toiture)
   - cf reference_data/thermal_inertia.json. C'est le SEUL facteur reellement norme en
   reglementation. Ce resultat (`Building.thermalInertiaClass`) n'est JAMAIS modifie par le
   mobilier.

2. `estimate_additional_thermal_mass` - mesure QUALITATIVE et distincte (mobilier/elements
   massifs : cheminee en pierre, poele de masse, chape beton apparente, mobilier massif en
   bois...), issue d'une reponse au questionnaire et/ou d'indices detectes par l'analyse vision
   des photos. Affichee SEPAREMENT dans le rapport (`Building.additionalThermalMassEstimate`) -
   **ne corrige jamais** la classe d'inertie ci-dessus, qui reste le seul facteur reglementaire
   (RE2020/RT ne comptabilisent que les parois, jamais le mobilier).

   Ce n'est PAS pour autant une simple "note secondaire sans valeur" : en approche
   bioclimatique/maison passive, la masse interieure (mobilier compris) contribue reellement a
   l'amortissement des variations de temperature et au confort d'ete (limitation du risque de
   surchauffe) - un phenomene physique reel, juste non comptabilise par le calcul reglementaire.
   Les deux mesures sont donc vraies et complementaires, chacune utile a un usage different :
   - `thermalInertiaClass` (parois)              -> calcul reglementaire normalise.
   - `additionalThermalMassEstimate` (mobilier)   -> indicateur qualitatif de confort d'ete /
                                                      risque de surchauffe, hors conformite
                                                      reglementaire.
"""
from app.shared.schemas import AdditionalThermalMassLevel, BuildingModel, ThermalInertiaClass, Wall
from app.thermal_engine.reference_data_loader import load_thermal_inertia

_SCORE_BY_WEIGHT = {"light": 1, "medium": 2, "heavy": 3}


def _wall_area(wall: Wall, floor_area: float, ceiling_height: float) -> float:
    if wall.kind == "exterior":
        return (wall.length_m or 0) * (wall.height_m or ceiling_height)
    return floor_area  # floor / roof


def _wall_weight_score(wall: Wall) -> int:
    """Determine le poids (1=leger, 2=moyen, 3=lourd) d'une paroi, a partir de ses couches de
    materiau si connues, sinon de sa typologie de construction (parois exterieures) ou d'une
    valeur neutre par defaut (plancher/toiture sans donnee)."""
    inertia_data = load_thermal_inertia()
    material_weights = inertia_data["material_weights"]

    layer_scores = [
        _SCORE_BY_WEIGHT[material_weights[layer.material_ref]]
        for layer in wall.layers
        if layer.material_ref and layer.material_ref in material_weights
    ]
    if layer_scores:
        return max(layer_scores)  # la couche la plus dense domine la contribution a l'inertie

    if wall.kind == "exterior":
        construction_weights = inertia_data["construction_type_weights"]
        weight = construction_weights.get(wall.construction_type, construction_weights["unknown"])
        return _SCORE_BY_WEIGHT[weight]

    return _SCORE_BY_WEIGHT["medium"]  # plancher/toiture sans donnee : hypothese neutre


def _classify_structural_score(avg_score: float) -> ThermalInertiaClass:
    thresholds = load_thermal_inertia()["class_thresholds"]
    if avg_score <= thresholds["light_max"]:
        return "light"
    if avg_score <= thresholds["medium_max"]:
        return "medium"
    return "heavy"


def compute_structural_inertia_class(building: BuildingModel) -> tuple[ThermalInertiaClass | None, list[str]]:
    """
    Classe d'inertie normee (parois uniquement). Retourne (classe, notes) - classe=None si le
    batiment n'a pas encore de parois (modele non genere). Les notes sont a fusionner dans le
    champ "assumptions" du rapport thermique.
    """
    weighted_score_sum = 0.0
    weighted_area_sum = 0.0

    for floor in building.floors:
        for room in floor.rooms:
            box = room.bounding_box
            floor_area = box.width_m * box.depth_m
            for wall in room.walls:
                if wall.kind not in ("exterior", "floor", "roof"):
                    continue
                area = _wall_area(wall, floor_area, box.height_m)
                if area <= 0:
                    continue
                weighted_score_sum += area * _wall_weight_score(wall)
                weighted_area_sum += area

    if weighted_area_sum == 0:
        return None, []

    avg_score = weighted_score_sum / weighted_area_sum
    structural_class = _classify_structural_score(avg_score)

    notes = [
        f"Classe d'inertie thermique (parois) = {structural_class} (score moyen pondere par "
        f"surface {avg_score:.2f}/3, base sur les materiaux/typologies des parois exterieures/"
        "plancher/toiture - seul facteur norme en reglementation RE2020, methode simplifiee a 3 "
        "classes ici contre 5 classes officielles avec Cm en J/m2.K). Ce resultat n'est jamais "
        "modifie par le mobilier - cf estimation separee ci-dessous."
    ]
    return structural_class, notes


def estimate_additional_thermal_mass(
    heavy_mass_questionnaire_hint: str | None = None,
    heavy_mass_vision_hints: list[str] | None = None,
) -> tuple[AdditionalThermalMassLevel | None, list[str]]:
    """
    Estimation QUALITATIVE et INDEPENDANTE du mobilier/des elements massifs presents (cheminee en
    pierre, poele de masse, chape beton apparente...). Indicateur de confort d'ete/risque de
    surchauffe en approche bioclimatique - PAS un facteur de conformite reglementaire. Ne corrige
    JAMAIS compute_structural_inertia_class - affichee a cote, comme une mesure distincte.
    Retourne (niveau, notes) - niveau=None si aucun indice disponible (ni questionnaire, ni vision).
    """
    hint_count = len(heavy_mass_vision_hints or [])

    if heavy_mass_questionnaire_hint == "significant" or hint_count >= 2:
        level: AdditionalThermalMassLevel | None = "significant"
    elif heavy_mass_questionnaire_hint == "some" or hint_count == 1:
        level = "notable"
    elif heavy_mass_questionnaire_hint == "none":
        level = "low"
    else:
        level = None  # aucun indice disponible (question pas encore posee, aucune photo analysee)

    if level is None:
        return None, []

    notes = [
        f"Masse thermique complementaire (mobilier) estimee a '{level}' - basee sur le "
        "questionnaire et/ou des elements detectes par l'analyse vision des photos (cheminee en "
        "pierre, poele de masse, chape beton apparente, mobilier massif en bois...). Indicateur "
        "QUALITATIF de confort d'ete / risque de surchauffe (approche bioclimatique - la masse "
        "interieure amortit reellement les variations de temperature), HORS calcul reglementaire "
        "RE2020/RT (qui ne comptabilise que les parois dans thermalInertiaClass). N'ajuste ni ne "
        "remplace thermalInertiaClass - deux mesures distinctes, chacune vraie dans son usage."
    ]
    return level, notes


DYNAMIC_INTEGRATION_NOTE = (
    "L'effet de l'inertie (parois) et de la masse thermique additionnelle (mobilier) sur le "
    "besoin de chauffage reel (dephasage/amortissement, meilleure utilisation des apports "
    "solaires/internes) N'EST PAS applique au calcul kWh/m2/an ci-dessus : le modeliser "
    "correctement necessite soit une methode a facteur d'utilisation des apports dependant de "
    "l'inertie (type Th-C-E simplifiee), soit une simulation thermique dynamique (STD) - hors "
    "scope de ce moteur simplifie V1. Point d'integration identifie pour V2 plutot qu'une "
    "correction approximative non fondee."
)
