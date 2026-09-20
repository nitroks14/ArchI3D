import type { QuestionnaireRepository } from "@/domain/repositories/QuestionnaireRepository";

export const runQuestionnaireStep = (repo: QuestionnaireRepository) => ({
  next: (projectId: string) => repo.getNextQuestion(projectId),
  answer: (projectId: string, field: string, value: string) => repo.answerQuestion(projectId, field, value),
});
