"""Tests de la classe d'inertie thermique simplifiee - purement unitaires, aucun appel reseau/IA."""
from app.shared.schemas import BuildingModel, Floor, MaterialLayer, Room, RoomBoundingBox, Wall
from app.thermal_engine.inertia import compute_thermal_inertia


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


def test_wood_frame_building_is_classified_light():
    building = _building_with_construction_type("wood_frame")
    inertia_class, notes = compute_thermal_inertia(building)
    assert inertia_class == "light"
    assert any("inertie" in note.lower() for note in notes)


def test_stone_building_is_classified_heavy():
    building = _building_with_construction_type("stone")
    inertia_class, _ = compute_thermal_inertia(building)
    assert inertia_class == "heavy"


def test_no_walls_returns_none_class_and_no_notes():
    empty = BuildingModel(project_id="test")
    inertia_class, notes = compute_thermal_inertia(empty)
    assert inertia_class is None
    assert notes == []


def test_significant_questionnaire_hint_bumps_class_up_by_one():
    building = _building_with_construction_type("wood_frame")  # -> "light" sans correction
    inertia_class, notes = compute_thermal_inertia(
        building, heavy_mass_questionnaire_hint="significant"
    )
    assert inertia_class == "medium"
    assert any("CORRECTION INDICATIVE NON NORMEE" in note for note in notes)


def test_heavy_class_is_not_bumped_beyond_heavy():
    building = _building_with_construction_type("stone")  # -> "heavy" deja au maximum
    inertia_class, _ = compute_thermal_inertia(building, heavy_mass_questionnaire_hint="significant")
    assert inertia_class == "heavy"


def test_two_vision_hints_also_bump_class_like_questionnaire():
    building = _building_with_construction_type("wood_frame")
    inertia_class, _ = compute_thermal_inertia(
        building, heavy_mass_vision_hints=["cheminee en pierre", "chape beton apparente"]
    )
    assert inertia_class == "medium"


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

    inertia_class, _ = compute_thermal_inertia(building)
    # Le plancher/toiture sans donnee restent neutres ("medium"), la moyenne ponderee par surface
    # ne peut donc pas tomber a "light" pur, mais doit rester strictement sous "heavy".
    assert inertia_class in ("light", "medium")
