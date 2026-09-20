"""
Classe d'inertie thermique simplifiee (leger/moyen/lourd), inspiree de l'approche RE2020 sans en
reprendre la methode complete (5 classes normees Th-I, Cm en J/m2.K...).

Deux facteurs :
1. **Parois structurelles** (dominant, seul facteur reellement norme en reglementation) : derive
   de la masse surfacique approximative des materiaux/typologies des parois exposees cote
   interieur (murs exterieurs, planchers, toiture) - cf reference_data/thermal_inertia.json.
2. **Mobilier/elements massifs** (secondaire, QUALITATIF) : une reponse au questionnaire et/ou
   des indices detectes par l'analyse vision des photos (cheminee en pierre, poele de masse,
   chape beton apparente, mobilier massif en bois...) peuvent faire basculer la classe calculee
   a l'etape 1 d'un cran vers le haut. **Ce facteur est une correction indicative uniquement** -
   les methodes reglementaires RE2020/RT ne comptabilisent PAS le mobilier dans le calcul
   officiel d'inertie (seulement les parois). Toujours distingue dans les assumptions retournees.
"""
from app.shared.schemas import BuildingModel, ThermalInertiaClass, Wall
from app.thermal_engine.reference_data_loader import load_construction_types, load_thermal_inertia

_SCORE_BY_WEIGHT = {"light": 1, "medium": 2, "heavy": 3}
_CLASS_BY_SCORE = {1: "light", 2: "medium", 3: "heavy"}


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


def _bump_class(current: ThermalInertiaClass) -> ThermalInertiaClass:
    order: list[ThermalInertiaClass] = ["light", "medium", "heavy"]
    idx = order.index(current)
    return order[min(idx + 1, len(order) - 1)]


def compute_thermal_inertia(
    building: BuildingModel,
    heavy_mass_questionnaire_hint: str | None = None,
    heavy_mass_vision_hints: list[str] | None = None,
) -> tuple[ThermalInertiaClass | None, list[str]]:
    """
    Retourne (classe, notes) - classe=None si le batiment n'a pas encore de parois (modele non
    genere). Les notes sont a fusionner dans le champ "assumptions" du rapport thermique.
    """
    load_construction_types()  # verifie que le catalogue est bien charge (coherence des cles)

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
        f"Classe d'inertie thermique = {structural_class} (score moyen pondere par surface "
        f"{avg_score:.2f}/3, base sur les materiaux/typologies des parois exterieures/plancher/"
        "toiture - seul facteur norme en reglementation RE2020, methode simplifiee a 3 classes "
        "ici contre 5 classes officielles avec Cm en J/m2.K)."
    ]

    final_class = structural_class
    heavy_hint_count = len(heavy_mass_vision_hints or [])
    if heavy_mass_questionnaire_hint == "significant" or heavy_hint_count >= 2:
        final_class = _bump_class(structural_class)
        notes.append(
            "Classe revue a la hausse (mobilier/elements massifs importants signales au "
            "questionnaire et/ou detectes sur plusieurs photos - cheminee en pierre, poele de "
            "masse, chape beton apparente...). CORRECTION INDICATIVE NON NORMEE : les methodes "
            "reglementaires RE2020/RT ne comptabilisent que les parois dans le calcul officiel "
            "d'inertie, jamais le mobilier."
        )
    elif heavy_mass_questionnaire_hint == "some" or heavy_hint_count == 1:
        notes.append(
            "Quelques elements massifs signales (mobilier/cheminee/poele) mais insuffisants pour "
            "faire basculer la classe calculee - indice qualitatif, non pris en compte dans le "
            "calcul officiel RE2020/RT (parois uniquement)."
        )

    notes.append(
        "L'effet de l'inertie sur le besoin de chauffage reel (dephasage/amortissement, "
        "meilleure utilisation des apports solaires/internes) N'EST PAS applique au calcul "
        "kWh/m2/an ci-dessus : le modeliser correctement necessite soit une methode a facteur "
        "d'utilisation des apports dependant de l'inertie (type Th-C-E simplifiee), soit une "
        "simulation thermique dynamique (STD) - hors scope de ce moteur simplifie V1. Point "
        "d'integration identifie pour V2 plutot qu'une correction approximative non fondee."
    )

    return final_class, notes
