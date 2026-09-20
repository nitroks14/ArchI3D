"""
Questionnaire IA progressif - moteur a regles V1 (deterministe, pas d'appel LLM) qui inspecte
le modele hierarchique et retourne la prochaine information manquante a demander a l'utilisateur.
Le nom de piece est TOUJOURS propose par l'IA (OCR plan + vision photos) mais reste editable/
a valider ici, conformement a la consigne produit.
"""
from app.questionnaire.schemas import Question, QuestionOption
from app.shared.schemas import BuildingModel, Opening
from app.thermal_engine.reference_data_loader import load_construction_types, load_glazing

HEATING_OPTIONS = [
    ("electric", "Chauffage electrique (radiateurs/convecteurs)"),
    ("heat_pump", "Pompe a chaleur"),
    ("gas", "Chaudiere gaz"),
    ("oil", "Chaudiere fioul"),
    ("wood", "Bois / poele / insert"),
    ("other", "Autre / inconnu"),
]

GLAZING_OPTIONS = [
    ("none", "Pas de fenetre exterieure dans cette piece"),
    ("single", "Simple vitrage"),
    ("double_pvc", "Double vitrage PVC"),
    ("double_alu", "Double vitrage aluminium"),
    ("double_wood", "Double vitrage bois"),
    ("triple", "Triple vitrage"),
]

# Facteur secondaire QUALITATIF d'inertie thermique (cf app/thermal_engine/inertia.py) - a ne
# jamais confondre avec le facteur structurel norme (parois), calcule automatiquement.
HEAVY_THERMAL_MASS_OPTIONS = [
    ("none", "Aucun / peu d'elements massifs"),
    ("some", "Quelques elements (ex: une cheminee ou un poele en pierre/beton)"),
    ("significant", "Beaucoup d'elements massifs (cheminee en pierre, poele de masse, chape beton apparente, mobilier massif en bois...)"),
]


def get_next_question(building: BuildingModel, answers: dict[str, str]) -> Question | None:
    for floor in building.floors:
        for room in floor.rooms:
            if not room.name_confirmed:
                return Question(
                    id=f"q_name_{room.id}",
                    field=f"room:{room.id}:name",
                    text=(
                        f'L\'IA propose le nom "{room.name}" pour cette piece '
                        f"(a partir du plan et des photos associees). Confirme ou corrige-le :"
                    ),
                    type="text",
                    context_label=room.name,
                )

            exterior_wall = next((w for w in room.walls if w.kind == "exterior"), None)
            if exterior_wall and exterior_wall.construction_type == "unknown":
                catalog = load_construction_types()
                options = [
                    QuestionOption(value=key, label=entry["label"], image_url=f"/reference-assets/{entry['image_asset']}")
                    for key, entry in catalog.items()
                    if key != "unknown"
                ]
                return Question(
                    id=f"q_construction_{exterior_wall.id}",
                    field=f"wall:{exterior_wall.id}:construction_type",
                    text=f'Quel type de construction correspond le mieux aux murs exterieurs de "{room.name}" ?',
                    type="single_choice",
                    options=options,
                    context_label=room.name,
                )

            if exterior_wall and not exterior_wall.openings:
                return Question(
                    id=f"q_glazing_{exterior_wall.id}",
                    field=f"wall:{exterior_wall.id}:glazing",
                    text=f'"{room.name}" a-t-elle des fenetres exterieures ? Si oui, quel type de vitrage ?',
                    type="single_choice",
                    options=[QuestionOption(value=v, label=label) for v, label in GLAZING_OPTIONS],
                    context_label=room.name,
                )

    if "building:heating_type" not in answers:
        return Question(
            id="q_heating_type",
            field="building:heating_type",
            text="Quel est le systeme de chauffage principal du logement ?",
            type="single_choice",
            options=[QuestionOption(value=v, label=label) for v, label in HEATING_OPTIONS],
        )

    if "building:heavy_thermal_mass" not in answers:
        return Question(
            id="q_heavy_thermal_mass",
            field="building:heavy_thermal_mass",
            text=(
                "Ton logement contient-il des elements massifs importants (cheminee en pierre, "
                "poele de masse, chape beton apparente, beaucoup de mobilier massif en bois) ? "
                "Cette info affine legerement la classe d'inertie thermique calculee automatiquement "
                "a partir des parois - elle reste indicative, contrairement aux parois qui sont le "
                "seul facteur reellement pris en compte par les methodes reglementaires."
            ),
            type="single_choice",
            options=[
                QuestionOption(value=v, label=label) for v, label in HEAVY_THERMAL_MASS_OPTIONS
            ],
        )

    return None


def apply_answer(building: BuildingModel, field: str, value: str) -> None:
    parts = field.split(":")

    if parts[0] == "room" and parts[2] == "name":
        room = _find_room(building, parts[1])
        room.name = value
        room.name_confirmed = True
        return

    if parts[0] == "wall" and parts[2] == "construction_type":
        wall = _find_wall(building, parts[1])
        wall.construction_type = value
        return

    if parts[0] == "wall" and parts[2] == "glazing":
        wall = _find_wall(building, parts[1])
        if value != "none":
            uw = load_glazing().get(value, {}).get("uw_w_per_m2k")
            wall.openings.append(Opening(type="window", glazing_type=value, uw_value=uw))
        return

    if field in ("building:heating_type", "building:heavy_thermal_mass"):
        return  # stocke uniquement dans questionnaire_answers (cf router), pas de champ dedie V1

    raise ValueError(f"Champ de questionnaire non reconnu : {field}")


def _find_room(building: BuildingModel, room_id: str):
    for floor in building.floors:
        for room in floor.rooms:
            if room.id == room_id:
                return room
    raise ValueError(f"Piece introuvable : {room_id}")


def _find_wall(building: BuildingModel, wall_id: str):
    for floor in building.floors:
        for room in floor.rooms:
            for wall in room.walls:
                if wall.id == wall_id:
                    return wall
    raise ValueError(f"Paroi introuvable : {wall_id}")
