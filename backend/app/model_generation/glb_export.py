"""
Export d'un BuildingModel (boites par piece) + des annexes de la parcelle en GLB, pour affichage
dans le viewer Three.js. Batiment principal et annexes partagent le meme repere local (metres) -
cf app/annexes/schemas.py pour le detail de cette convention.
"""
import math

import trimesh

from app.annexes.schemas import Annex
from app.shared.schemas import BuildingModel

STORY_HEIGHT_M = 2.7  # hauteur generique utilisee pour empiler les etages dans le viewer


def build_glb(building: BuildingModel, annexes: list[Annex] | None = None) -> bytes:
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

    for annex in annexes or []:
        mesh = trimesh.creation.box(extents=(annex.width_m, annex.depth_m, annex.height_m))
        if annex.rotation_deg:
            mesh.apply_transform(
                trimesh.transformations.rotation_matrix(math.radians(annex.rotation_deg), [0, 0, 1])
            )
        translation = [
            annex.offset_x_m + annex.width_m / 2,
            annex.offset_y_m + annex.depth_m / 2,
            annex.height_m / 2,
        ]
        mesh.apply_translation(translation)
        scene.add_geometry(mesh, node_name=annex.id)

    return scene.export(file_type="glb")
