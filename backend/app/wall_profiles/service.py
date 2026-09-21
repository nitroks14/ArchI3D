"""
Capture, suggestion et application groupee des profils de paroi reutilisables (cf schemas.py).

Correspondance volontairement simple pour la V1 (pas d'heuristique sophistiquee) : meme type de
paroi (exterieure/interieure/plancher/toiture), priorite aux profils deja utilises sur le meme
etage, repli sur le profil le plus recemment utilise tous etages confondus.
"""
from datetime import UTC, datetime

from app.shared.schemas import BuildingModel, Floor, Room, Wall
from app.wall_profiles.schemas import WallAssemblyProfile


def find_wall_context(building: BuildingModel, wall_id: str) -> tuple[Floor, Room, Wall] | None:
    for floor in building.floors:
        for room in floor.rooms:
            for wall in room.walls:
                if wall.id == wall_id:
                    return floor, room, wall
    return None


def _layer_signature(layer) -> tuple:
    return (layer.material_ref, layer.thickness_cm, layer.r_value)


def _profile_signature(kind: str, construction_type: str, layers: list) -> tuple:
    return (kind, construction_type, tuple(sorted(_layer_signature(layer) for layer in layers)))


def _generate_label(wall: Wall) -> str:
    from app.thermal_engine.reference_data_loader import load_construction_types

    catalog = load_construction_types()
    base_label = catalog.get(wall.construction_type, catalog["unknown"])["label"]
    if wall.layers:
        materials = ", ".join(
            f"{layer.material_ref}" for layer in wall.layers if layer.material_ref
        )
        if materials:
            return f"{base_label} ({materials})"
    return base_label


def upsert_profile_from_wall(
    profiles: list[WallAssemblyProfile], wall: Wall
) -> WallAssemblyProfile | None:
    """
    Capture (ou incremente si deja connu) un profil reutilisable a partir de l'etat actuel d'une
    paroi. Appele des qu'une paroi recoit une donnee exploitable (reponse au questionnaire,
    facture liee...). Ne fait rien si la paroi n'a encore aucune information utile. Mute `profiles`
    en place (liste appartenant a ProjectState.wallAssemblyProfiles cote appelant).
    """
    if wall.construction_type == "unknown" and not wall.layers:
        return None

    signature = _profile_signature(wall.kind, wall.construction_type, wall.layers)
    for profile in profiles:
        profile_signature = _profile_signature(
            profile.applicable_wall_kind, profile.construction_type, profile.layers
        )
        if profile_signature == signature:
            profile.usage_count += 1
            profile.last_used_at = datetime.now(UTC).isoformat()
            return profile

    source = wall.layers[0].source if wall.layers else "user_input"
    profile = WallAssemblyProfile(
        label=_generate_label(wall),
        applicable_wall_kind=wall.kind,
        construction_type=wall.construction_type,
        layers=[layer.model_copy() for layer in wall.layers],
        source=source,
    )
    profiles.append(profile)
    return profile


def suggest_profile_for_wall(
    profiles: list[WallAssemblyProfile], building: BuildingModel, wall_id: str
) -> WallAssemblyProfile | None:
    """Suggestion de pre-remplissage pour une paroi donnee - jamais applique automatiquement,
    juste propose (cf Question.suggestedValue, a valider/corriger par l'utilisateur)."""
    context = find_wall_context(building, wall_id)
    if context is None:
        return None
    target_floor, _room, target_wall = context

    candidates = [p for p in profiles if p.applicable_wall_kind == target_wall.kind]
    if not candidates:
        return None

    same_floor_ids = {
        w.id
        for room in target_floor.rooms
        for w in room.walls
        if w.kind == target_wall.kind and w.construction_type != "unknown"
    }
    # Priorite aux profils dont la signature correspond a une paroi deja posee sur le meme etage.
    same_floor_signatures = {
        _profile_signature(w.kind, w.construction_type, w.layers)
        for room in target_floor.rooms
        for w in room.walls
        if w.id in same_floor_ids
    }
    same_floor_candidates = [
        p
        for p in candidates
        if _profile_signature(p.applicable_wall_kind, p.construction_type, p.layers) in same_floor_signatures
    ]

    pool = same_floor_candidates or candidates
    return max(pool, key=lambda p: p.last_used_at)


def apply_profile_to_unset_walls(
    profiles: list[WallAssemblyProfile], building: BuildingModel, profile_id: str, wall_kind: str
) -> int:
    """Action groupee explicite (jamais automatique) : applique un profil a toutes les parois du
    type donne qui n'ont encore ni typologie ni couche renseignee. Retourne le nombre de parois
    modifiees."""
    profile = next((p for p in profiles if p.id == profile_id), None)
    if profile is None:
        raise ValueError(f"Profil introuvable : {profile_id}")

    applied = 0
    for floor in building.floors:
        for room in floor.rooms:
            for wall in room.walls:
                if wall.kind != wall_kind:
                    continue
                if wall.construction_type != "unknown" or wall.layers:
                    continue  # deja renseignee individuellement - on ne l'ecrase jamais
                wall.construction_type = profile.construction_type
                wall.layers = [layer.model_copy() for layer in profile.layers]
                applied += 1

    if applied:
        profile.usage_count += applied
        profile.last_used_at = datetime.now(UTC).isoformat()

    return applied
