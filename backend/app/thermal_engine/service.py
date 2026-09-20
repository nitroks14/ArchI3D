"""
Moteur de calcul thermique/energetique SIMPLIFIE V1.

Objectif : donner un ordre de grandeur exploitable (Ubat approche, kWh/m2/an indicatif) a
partir du modele hierarchique + de la bibliotheque de valeurs par defaut (reference_data/).

Ce N'EST PAS un moteur reglementaire (pas de methode Th-BCE, pas de zone climatique, pas de
scenario d'occupation RE2020). Toutes les hypotheses de calcul sont listees dans le champ
"assumptions" de la reponse pour rester transparent sur ce qui est indicatif. Cf README > roadmap V2.
"""
from app.climate.factory import get_climate_data_provider
from app.shared.schemas import BuildingModel, Room, Wall
from app.thermal_engine.inertia import (
    DYNAMIC_INTEGRATION_NOTE,
    compute_structural_inertia_class,
    estimate_additional_thermal_mass,
)
from app.thermal_engine.reference_data_loader import (
    load_construction_types,
    load_glazing,
    load_materials,
    load_thermal_bridges,
)

DJU_DEFAULT = 2200  # degres-jours unifies base 18, moyenne climat France - pas de zone climatique en V1
OTHER_USES_KWH_PER_M2 = 30  # ECS + auxiliaires + eclairage, forfait indicatif V1
DEFAULT_FLOOR_U = 0.40  # W/m2.K, plancher bas non renseigne
DEFAULT_ROOF_U = 0.25  # W/m2.K, toiture/plancher haut non renseigne


def _wall_layers_u_value(wall: Wall) -> float | None:
    materials = load_materials()
    total_r = 0.0
    has_data = False
    for layer in wall.layers:
        if layer.r_value:
            total_r += layer.r_value
            has_data = True
        elif layer.thickness_cm and layer.material_ref and layer.material_ref in materials:
            lam = materials[layer.material_ref]["lambda_w_per_mk"]
            total_r += (layer.thickness_cm / 100) / lam
            has_data = True
    if has_data and total_r > 0:
        return 1 / total_r
    return None


def _opening_uw(opening) -> float:
    if opening.uw_value:
        return opening.uw_value
    glazing = load_glazing()
    entry = glazing.get(opening.glazing_type or "unknown", glazing["unknown"])
    return entry["uw_w_per_m2k"]


def _room_contribution(room: Room) -> dict:
    construction_types = load_construction_types()
    box = room.bounding_box
    floor_area = box.width_m * box.depth_m

    walls_h, roof_h, floor_h, windows_h, bridges_h = 0.0, 0.0, 0.0, 0.0, 0.0
    bridges = load_thermal_bridges()

    for wall in room.walls:
        if wall.kind == "exterior":
            gross_area = (wall.length_m or 0) * (wall.height_m or box.height_m)
            openings_area = sum(o.width_m * o.height_m for o in wall.openings)
            net_area = max(gross_area - openings_area, 0)

            u_value = _wall_layers_u_value(wall)
            if u_value is None:
                entry = construction_types.get(wall.construction_type, construction_types["unknown"])
                u_value = entry["default_wall_u_value"]
            walls_h += net_area * u_value

            for opening in wall.openings:
                windows_h += opening.width_m * opening.height_m * _opening_uw(opening)
                perimeter = 2 * (opening.width_m + opening.height_m)
                bridges_h += perimeter * bridges["wall_opening"]["psi_w_per_mk"]

            bridges_h += (wall.length_m or 0) * bridges["wall_floor"]["psi_w_per_mk"]
            bridges_h += (wall.length_m or 0) * bridges["wall_roof"]["psi_w_per_mk"]

        elif wall.kind == "floor":
            u_value = _wall_layers_u_value(wall) or DEFAULT_FLOOR_U
            floor_h += floor_area * u_value

        elif wall.kind == "roof":
            u_value = _wall_layers_u_value(wall) or DEFAULT_ROOF_U
            roof_h += floor_area * u_value

    return {
        "floor_area_m2": floor_area,
        "walls_w_per_k": walls_h,
        "roof_w_per_k": roof_h,
        "floor_w_per_k": floor_h,
        "windows_w_per_k": windows_h,
        "thermal_bridges_w_per_k": bridges_h,
    }


def _resolve_dju(building: BuildingModel) -> tuple[float, str]:
    """
    Utilise le DJU reel (Open-Meteo) si le batiment est geolocalise, sinon la constante
    nationale moyenne DJU_DEFAULT. Voir app/geolocation pour renseigner latitude/longitude
    (geocodage d'adresse ou pin manuel).
    """
    if building.latitude is None or building.longitude is None:
        return DJU_DEFAULT, "constante nationale moyenne (batiment non geolocalise)"

    summary = get_climate_data_provider().get_climate_summary(building.latitude, building.longitude)
    return summary.estimated_dju_base18, summary.data_source


def compute_thermal_report(
    building: BuildingModel,
    heavy_mass_questionnaire_hint: str | None = None,
    heavy_mass_vision_hints: list[str] | None = None,
) -> dict:
    dju, dju_source = _resolve_dju(building)

    # Deux mesures INDEPENDANTES, jamais fusionnees (cf app/thermal_engine/inertia.py) : la
    # classe d'inertie (parois, normee) n'est jamais modifiee par l'estimation qualitative du
    # mobilier - elles sont calculees separement et affichees cote a cote dans le rapport.
    inertia_class, inertia_notes = compute_structural_inertia_class(building)
    building.thermal_inertia_class = inertia_class

    additional_mass_level, additional_mass_notes = estimate_additional_thermal_mass(
        heavy_mass_questionnaire_hint, heavy_mass_vision_hints
    )
    building.additional_thermal_mass_estimate = additional_mass_level

    totals = {
        "floor_area_m2": 0.0,
        "walls_w_per_k": 0.0,
        "roof_w_per_k": 0.0,
        "floor_w_per_k": 0.0,
        "windows_w_per_k": 0.0,
        "thermal_bridges_w_per_k": 0.0,
    }

    for floor in building.floors:
        for room in floor.rooms:
            contribution = _room_contribution(room)
            for key in totals:
                totals[key] += contribution[key]

    total_h = (
        totals["walls_w_per_k"]
        + totals["roof_w_per_k"]
        + totals["floor_w_per_k"]
        + totals["windows_w_per_k"]
        + totals["thermal_bridges_w_per_k"]
    )
    ubat = None
    annual_heating_kwh = total_h * dju * 24 / 1000
    estimated_kwh_per_m2 = None
    if totals["floor_area_m2"] > 0:
        ubat = total_h / (totals["floor_area_m2"] * 3)  # approx surface enveloppe ~ 3x surface au sol
        estimated_kwh_per_m2 = annual_heating_kwh / totals["floor_area_m2"] + OTHER_USES_KWH_PER_M2

    return {
        "floor_area_m2": round(totals["floor_area_m2"], 1),
        "total_heat_loss_coefficient_w_per_k": round(total_h, 1),
        "breakdown_w_per_k": {
            "walls": round(totals["walls_w_per_k"], 1),
            "roof": round(totals["roof_w_per_k"], 1),
            "floor": round(totals["floor_w_per_k"], 1),
            "windows": round(totals["windows_w_per_k"], 1),
            "thermal_bridges": round(totals["thermal_bridges_w_per_k"], 1),
        },
        "ubat_w_per_m2k": round(ubat, 2) if ubat else None,
        "dju_used": dju,
        "dju_source": dju_source,
        "estimated_annual_heating_kwh": round(annual_heating_kwh, 0),
        "estimated_kwh_per_m2_per_year": (
            round(estimated_kwh_per_m2, 0) if estimated_kwh_per_m2 else None
        ),
        "thermal_inertia_class": inertia_class,
        "additional_thermal_mass_estimate": additional_mass_level,
        "assumptions": [
            "Valeurs indicatives de degrossissage - PAS une etude thermique reglementaire "
            "(pas de methode Th-BCE/RE2020 complete).",
            f"Degres-jours unifies (DJU) = {dju:.0f}, source : {dju_source}.",
            "Tout le perimetre de chaque piece est considere comme paroi exterieure "
            "(l'heuristique V1 ne detecte pas les murs mitoyens entre pieces) - surestime "
            "les deperditions des pieces interieures.",
            f"Plancher bas par defaut U={DEFAULT_FLOOR_U} W/m2.K et toiture par defaut "
            f"U={DEFAULT_ROOF_U} W/m2.K si non renseignes via facture/questionnaire.",
            f"Poste ECS + auxiliaires + eclairage forfaitise a {OTHER_USES_KWH_PER_M2} kWh/m2/an.",
            "Ubat approxime en supposant une surface d'enveloppe totale ~= 3x la surface au "
            "sol (murs+plancher+toiture).",
            *inertia_notes,
            *additional_mass_notes,
            DYNAMIC_INTEGRATION_NOTE,
        ],
    }
