"""Tests de la bibliotheque de profils de parois reutilisables - purement unitaires."""
import pytest

from app.shared.schemas import BuildingModel, Floor, MaterialLayer, Room, RoomBoundingBox, Wall
from app.wall_profiles.service import (
    apply_profile_to_unset_walls,
    find_wall_context,
    suggest_profile_for_wall,
    upsert_profile_from_wall,
)


def _room(wall: Wall, room_id: str = "room_1", floor_id: str = "floor_1") -> Room:
    return Room(
        id=room_id,
        floor_id=floor_id,
        name="Salon",
        name_confirmed=True,
        bounding_box=RoomBoundingBox(x=0, y=0, width_m=5, depth_m=4, height_m=2.5),
        walls=[wall],
    )


def test_upsert_creates_new_profile_from_wall_with_construction_type():
    wall = Wall(id="wall_1", kind="exterior", construction_type="monomur", length_m=18, height_m=2.5)
    profiles: list = []

    profile = upsert_profile_from_wall(profiles, wall)

    assert profile is not None
    assert len(profiles) == 1
    assert profiles[0].construction_type == "monomur"
    assert profiles[0].usage_count == 1


def test_upsert_increments_usage_count_on_identical_signature():
    profiles: list = []
    wall_a = Wall(id="wall_a", kind="exterior", construction_type="monomur")
    wall_b = Wall(id="wall_b", kind="exterior", construction_type="monomur")

    upsert_profile_from_wall(profiles, wall_a)
    result = upsert_profile_from_wall(profiles, wall_b)

    assert len(profiles) == 1  # pas de doublon
    assert result.usage_count == 2


def test_upsert_returns_none_for_wall_without_usable_data():
    profiles: list = []
    wall = Wall(id="wall_1", kind="exterior", construction_type="unknown")

    result = upsert_profile_from_wall(profiles, wall)

    assert result is None
    assert profiles == []


def test_upsert_with_explicit_material_layer_creates_distinct_profile():
    profiles: list = []
    wall = Wall(
        id="wall_1",
        kind="exterior",
        construction_type="ite",
        layers=[MaterialLayer(material_ref="glass_wool", thickness_cm=12)],
    )

    profile = upsert_profile_from_wall(profiles, wall)

    assert profile.layers[0].material_ref == "glass_wool"


def test_suggest_returns_none_when_no_matching_kind():
    wall = Wall(id="wall_1", kind="exterior", construction_type="unknown")
    floor = Floor(id="floor_1", name="RDC", level=0, rooms=[_room(wall)])
    building = BuildingModel(project_id="test", floors=[floor])

    profiles: list = []
    suggestion = suggest_profile_for_wall(profiles, building, "wall_1")

    assert suggestion is None


def test_suggest_returns_matching_profile_for_same_wall_kind():
    known_wall = Wall(id="wall_known", kind="exterior", construction_type="monomur")
    new_wall = Wall(id="wall_new", kind="exterior", construction_type="unknown")
    rooms = [_room(known_wall, "room_1"), _room(new_wall, "room_2")]
    floor = Floor(id="floor_1", name="RDC", level=0, rooms=rooms)
    building = BuildingModel(project_id="test", floors=[floor])

    profiles: list = []
    upsert_profile_from_wall(profiles, known_wall)

    suggestion = suggest_profile_for_wall(profiles, building, "wall_new")

    assert suggestion is not None
    assert suggestion.construction_type == "monomur"


def test_find_wall_context_returns_floor_room_wall():
    wall = Wall(id="wall_1", kind="exterior", construction_type="stone")
    room = _room(wall)
    floor = Floor(id="floor_1", name="RDC", level=0, rooms=[room])
    building = BuildingModel(project_id="test", floors=[floor])

    context = find_wall_context(building, "wall_1")

    assert context is not None
    found_floor, found_room, found_wall = context
    assert found_floor.id == "floor_1"
    assert found_room.id == room.id
    assert found_wall.id == "wall_1"


def test_apply_profile_to_unset_walls_skips_already_set_walls():
    already_set = Wall(id="wall_set", kind="exterior", construction_type="stone")
    unset = Wall(id="wall_unset", kind="exterior", construction_type="unknown")
    floor = Floor(
        id="floor_1",
        name="RDC",
        level=0,
        rooms=[_room(already_set, "room_1"), _room(unset, "room_2")],
    )
    building = BuildingModel(project_id="test", floors=[floor])

    profiles: list = []
    profile = upsert_profile_from_wall(profiles, Wall(kind="exterior", construction_type="monomur"))

    applied_count = apply_profile_to_unset_walls(profiles, building, profile.id, "exterior")

    assert applied_count == 1
    assert unset.construction_type == "monomur"
    assert already_set.construction_type == "stone"  # jamais ecrasee


def test_apply_profile_to_unset_walls_raises_for_unknown_profile():
    building = BuildingModel(project_id="test")
    with pytest.raises(ValueError):
        apply_profile_to_unset_walls([], building, "profile_missing", "exterior")
