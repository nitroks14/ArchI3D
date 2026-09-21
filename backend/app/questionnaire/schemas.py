from typing import Literal

from app.shared.base import CamelModel


class QuestionOption(CamelModel):
    value: str
    label: str
    image_url: str | None = None  # utilise pour les options du catalogue de construction illustre


class Question(CamelModel):
    id: str
    field: str  # identifiant d'application de la reponse, ex: "room:room_ab12:name"
    text: str
    type: Literal["text", "single_choice", "construction_type_visual"]
    options: list[QuestionOption] = []
    context_label: str | None = None  # ex: nom de la piece concernee, pour affichage frontend
    # Pre-remplissage intelligent (cf app/wall_profiles) : une SUGGESTION a partir d'un profil
    # deja utilise ailleurs dans le projet - jamais une valeur validee automatiquement, toujours
    # modifiable/rejetable par l'utilisateur. suggestion_note explique d'ou vient la suggestion.
    suggested_value: str | None = None
    suggestion_note: str | None = None


class QuestionnaireState(CamelModel):
    done: bool
    question: Question | None = None


class AnswerRequest(CamelModel):
    field: str
    value: str
