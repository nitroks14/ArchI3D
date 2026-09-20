"""
Orchestration de la generation du modele de batiment hierarchique a partir d'un plan 2D,
puis export GLB pour le viewer 3D. Heuristique volontairement simple pour la V1
(cf plan_heuristic.py) - amelioration prevue en V2 (vectorisation fine, murs/ouvertures reels).
"""
from datetime import UTC, datetime

from app.annexes.schemas import Annex
from app.model_generation.glb_export import build_glb
from app.model_generation.plan_heuristic import detect_rooms
from app.model_generation.room_naming import guess_room_from_ocr_text
from app.projects.models import ProjectState
from app.shared.schemas import BuildingModel, Floor, Room, RoomBoundingBox, Wall
from app.storage.factory import get_storage_backend


def _default_walls(room: Room) -> list[Wall]:
    """
    Genere les parois par defaut d'une piece (exterieure/plancher/toiture), construction_type
    "unknown" en attendant le questionnaire ou une facture materiau.

    Simplification V1 assumee : l'heuristique de detection de pieces ne determine pas
    l'adjacence reelle entre pieces (mur exterieur vs mur mitoyen avec la piece voisine).
    On considere donc, par prudence, tout le perimetre de chaque piece comme expose (mur
    exterieur), ainsi qu'un plancher bas et une toiture par piece. Cela surestime les
    deperditions pour les pieces mitoyennes a l'interieur du batiment - affinage prevu en V2
    (vectorisation des plans avec detection des murs partages).
    """
    box = room.bounding_box
    perimeter_m = 2 * (box.width_m + box.depth_m)
    return [
        Wall(kind="exterior", length_m=round(perimeter_m, 2), height_m=box.height_m),
        Wall(kind="floor", length_m=None, height_m=None),
        Wall(kind="roof", length_m=None, height_m=None),
    ]


def generate_building_model(
    state: ProjectState,
    plan_id: str,
    floor_label: str,
    floor_level: int,
    meters_per_pixel: float,
    default_ceiling_height_m: float,
) -> BuildingModel:
    plan = next((p for p in state.plans if p.id == plan_id), None)
    if plan is None:
        raise ValueError(f"Plan introuvable : {plan_id}")

    image_bytes = get_storage_backend().read(plan.storage_key)
    detected_rooms = detect_rooms(image_bytes)

    floor = Floor(name=floor_label, level=floor_level, plan_id=plan_id)
    for index, detected in enumerate(detected_rooms, start=1):
        room_type, suggested_name = guess_room_from_ocr_text(detected.ocr_text)
        room = Room(
            floor_id=floor.id,
            name=suggested_name or f"Piece {index}",
            suggested_name=suggested_name,
            name_confirmed=False,
            room_type=room_type,
            bounding_box=RoomBoundingBox(
                x=detected.x_px * meters_per_pixel,
                y=detected.y_px * meters_per_pixel,
                width_m=round(detected.w_px * meters_per_pixel, 2),
                depth_m=round(detected.h_px * meters_per_pixel, 2),
                height_m=default_ceiling_height_m,
            ),
        )
        room.walls = _default_walls(room)
        floor.rooms.append(room)

    building = state.building_model or BuildingModel(project_id=state.id)
    building.floors = [f for f in building.floors if f.name != floor_label] + [floor]
    building.generated_at = datetime.now(UTC).isoformat()

    building.glb_url = regenerate_glb(state.id, building, state.annexes)

    return building


def regenerate_glb(project_id: str, building: BuildingModel, annexes: list[Annex]) -> str:
    """
    Reconstruit et sauvegarde l'export GLB (batiment + annexes de la parcelle). Reutilise a
    chaque generation/regeneration du modele de batiment ET a chaque creation/modification/
    suppression d'annexe (cf app/annexes/router.py), pour que le jumeau numerique 3D reste a
    jour sans etape manuelle supplementaire.
    """
    glb_bytes = build_glb(building, annexes)
    glb_key = f"{project_id}/model/building.glb"
    return get_storage_backend().save(glb_key, glb_bytes, "model/gltf-binary")
