"""Tests du moteur thermique simplifie - purement unitaires, aucun appel reseau/IA."""
from app.shared.schemas import BuildingModel, Floor, Room, RoomBoundingBox, Wall
from app.thermal_engine.service import compute_thermal_report


def _simple_building() -> BuildingModel:
    room = Room(
        floor_id="floor_1",
        name="Salon",
        name_confirmed=True,
        bounding_box=RoomBoundingBox(x=0, y=0, width_m=5, depth_m=4, height_m=2.5),
        walls=[
            Wall(kind="exterior", construction_type="ite", length_m=18, height_m=2.5),
            Wall(kind="floor"),
            Wall(kind="roof"),
        ],
    )
    floor = Floor(name="RDC", level=0, rooms=[room])
    return BuildingModel(project_id="test", floors=[floor])


def test_compute_thermal_report_returns_positive_heat_loss():
    report = compute_thermal_report(_simple_building())
    assert report["total_heat_loss_coefficient_w_per_k"] > 0
    assert report["floor_area_m2"] == 20.0
    assert report["ubat_w_per_m2k"] is not None
    assert report["estimated_kwh_per_m2_per_year"] is not None
    assert len(report["assumptions"]) > 0


def test_compute_thermal_report_empty_building_returns_zero():
    empty = BuildingModel(project_id="test")
    report = compute_thermal_report(empty)
    assert report["total_heat_loss_coefficient_w_per_k"] == 0
    assert report["estimated_kwh_per_m2_per_year"] is None
