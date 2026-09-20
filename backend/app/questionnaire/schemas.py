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


class QuestionnaireState(CamelModel):
    done: bool
    question: Question | None = None


class AnswerRequest(CamelModel):
    field: str
    value: str
