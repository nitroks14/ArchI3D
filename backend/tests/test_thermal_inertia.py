"""
Tests de l'inertie thermique - purement unitaires, aucun appel reseau/IA.

Deux mesures INDEPENDANTES testees separement, conformement a la consigne produit : la classe
d'inertie des parois (compute_structural_inertia_class) ne doit JAMAIS etre influencee par
l'estimation qualitative du mobilier (estimate_additional_thermal_mass).
"""
from app.shared.schemas import BuildingModel, Floor, MaterialLayer, Room, RoomBoundingBox, Wall
from app.thermal_engine.inertia import (
    compute_structural_inertia_class,
    estimate_additional_thermal_mass,
)


def _building_with_construction_type(construction_type: str) -> BuildingModel:
    room = Room(
        floor_id="floor_1",
        name="Salon",
        name_confirmed=True,
        bounding_box=RoomBoundingBox(x=0, y=0, width_m=5, depth_m=4, height_m=2.5),
        walls=[
            Wall(kind="exterior", construction_type=construction_type, length_m=18, height_m=2.5),
            Wall(kind="floor"),
            Wall(kind="roof"),
        ],
    )
    floor = Floor(name="RDC", level=0, rooms=[room])
    return BuildingModel(project_id="test", floors=[floor])


# --- compute_structural_inertia_class (parois, normee) ---


def test_wood_frame_building_is_classified_light():
    building = _building_with_construction_type("wood_frame")
    inertia_class, notes = compute_structural_inertia_class(building)
    assert inertia_class == "light"
    assert any("inertie" in note.lower() for note in notes)


def test_stone_building_is_classified_heavy():
    building = _building_with_construction_type("stone")
    inertia_class, _ = compute_structural_inertia_class(building)
    assert inertia_class == "heavy"


def test_no_walls_returns_none_class_and_no_notes():
    empty = BuildingModel(project_id="test")
    inertia_class, notes = compute_structural_inertia_class(empty)
    assert inertia_class is None
    assert notes == []


def test_explicit_material_layer_dominates_over_construction_type_default():
    # ITE (defaut "heavy") mais couche isolante explicite en laine de verre ("light") : la couche
    # renseignee doit l'emporter sur le defaut de typologie.
    room = Room(
        floor_id="floor_1",
        name="Salon",
        name_confirmed=True,
        bounding_box=RoomBoundingBox(x=0, y=0, width_m=5, depth_m=4, height_m=2.5),
        walls=[
            Wall(
                kind="exterior",
                construction_type="ite",
                length_m=18,
                height_m=2.5,
                layers=[MaterialLayer(material_ref="glass_wool", thickness_cm=12)],
            ),
            Wall(kind="floor"),
            Wall(kind="roof"),
        ],
    )
    floor = Floor(name="RDC", level=0, rooms=[room])
    building = BuildingModel(project_id="test", floors=[floor])

    inertia_class, _ = compute_structural_inertia_class(building)
    assert inertia_class in ("light", "medium")  # ne doit plus etre "heavy" (defaut ITE ecarte)


def test_structural_class_is_not_affected_by_heavy_furniture_signals():
    """Regression du correctif produit : le mobilier ne doit JAMAIS influencer les parois."""
    building = _building_with_construction_type("wood_frame")
    class_without_hint, _ = compute_structural_inertia_class(building)
    # compute_structural_inertia_class n'accepte meme plus de parametres lies au mobilier -
    # on verifie simplement que le resultat est stable et reste "light" (pas de bascule cachee).
    assert class_without_hint == "light"


# --- estimate_additional_thermal_mass (mobilier, qualitatif, confort d'ete) ---


def test_no_hint_returns_none():
    level, notes = estimate_additional_thermal_mass()
    assert level is None
    assert notes == []


def test_questionnaire_hint_none_maps_to_low():
    level, _ = estimate_additional_thermal_mass(heavy_mass_questionnaire_hint="none")
    assert level == "low"


def test_questionnaire_hint_some_maps_to_notable():
    level, _ = estimate_additional_thermal_mass(heavy_mass_questionnaire_hint="some")
    assert level == "notable"


def test_questionnaire_hint_significant_maps_to_significant():
    level, notes = estimate_additional_thermal_mass(heavy_mass_questionnaire_hint="significant")
    assert level == "significant"
    assert any("confort" in note.lower() for note in notes)


def test_two_vision_hints_map_to_significant_like_questionnaire():
    level, _ = estimate_additional_thermal_mass(
        heavy_mass_vision_hints=["cheminee en pierre", "chape beton apparente"]
    )
    assert level == "significant"


def test_single_vision_hint_maps_to_notable():
    level, _ = estimate_additional_thermal_mass(heavy_mass_vision_hints=["poele de masse"])
    assert level == "notable"
