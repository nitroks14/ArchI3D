"""Export d'un BuildingModel (boites par piece) en GLB pour affichage dans le viewer Three.js."""
import trimesh

from app.shared.schemas import BuildingModel

STORY_HEIGHT_M = 2.7  # hauteur generique utilisee pour empiler les etages dans le viewer


def build_glb(building: BuildingModel) -> bytes:
    scene = trimesh.Scene()

    for floor in building.floors:
        z_offset = floor.level * STORY_HEIGHT_M
        for room in floor.rooms:
            box = room.bounding_box
            mesh = trimesh.creation.box(extents=(box.width_m, box.depth_m, box.height_m))
            translation = [
                box.x + box.width_m / 2,
                box.y + box.depth_m / 2,
                z_offset + box.height_m / 2,
            ]
            mesh.apply_translation(translation)
            scene.add_geometry(mesh, node_name=room.id)

    return scene.export(file_type="glb")
