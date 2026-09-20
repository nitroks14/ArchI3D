import type { QuestionnaireRepository } from "@/domain/repositories/QuestionnaireRepository";
import type { QuestionnaireState } from "@/domain/model/Question";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpQuestionnaireRepository implements QuestionnaireRepository {
  getNextQuestion(projectId: string): Promise<QuestionnaireState> {
    return apiClient.get<QuestionnaireState>(`/projects/${projectId}/questionnaire/next`);
  }

  answerQuestion(projectId: string, field: string, value: string): Promise<QuestionnaireState> {
    return apiClient.postJson<QuestionnaireState>(`/projects/${projectId}/questionnaire/answer`, {
      field,
      value,
    });
  }
}
