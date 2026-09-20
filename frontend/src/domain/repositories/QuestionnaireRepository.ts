import type { QuestionnaireState } from "@/domain/model/Question";

export interface QuestionnaireRepository {
  getNextQuestion(projectId: string): Promise<QuestionnaireState>;
  answerQuestion(projectId: string, field: string, value: string): Promise<QuestionnaireState>;
}
