from fastapi import APIRouter, Depends, HTTPException

from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.questionnaire.schemas import AnswerRequest, QuestionnaireState
from app.questionnaire.service import apply_answer, get_next_question

router = APIRouter(prefix="/projects", tags=["questionnaire"])


@router.get("/{project_id}/questionnaire/next", response_model=QuestionnaireState)
def next_question(state: ProjectState = Depends(get_owned_project_state)) -> QuestionnaireState:
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Genere d'abord le modele 3D du batiment")
    question = get_next_question(state.building_model, state.questionnaire_answers)
    return QuestionnaireState(done=question is None, question=question)


@router.post("/{project_id}/questionnaire/answer", response_model=QuestionnaireState)
def answer_question(
    payload: AnswerRequest, state: ProjectState = Depends(get_owned_project_state)
) -> QuestionnaireState:
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Genere d'abord le modele 3D du batiment")

    try:
        apply_answer(state.building_model, payload.field, payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state.questionnaire_answers[payload.field] = payload.value
    get_project_store().save(state)

    question = get_next_question(state.building_model, state.questionnaire_answers)
    return QuestionnaireState(done=question is None, question=question)
