import type {
  GenerateModelParams,
  ModelGenerationRepository,
} from "@/domain/repositories/ModelGenerationRepository";

export const generateBuildingModel =
  (repo: ModelGenerationRepository) => (projectId: string, params: GenerateModelParams) =>
    repo.generateModel(projectId, params);
