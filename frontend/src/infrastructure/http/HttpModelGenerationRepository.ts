import type {
  GenerateModelParams,
  ModelGenerationRepository,
} from "@/domain/repositories/ModelGenerationRepository";
import type { BuildingModel } from "@/domain/model/Building";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpModelGenerationRepository implements ModelGenerationRepository {
  generateModel(projectId: string, params: GenerateModelParams): Promise<BuildingModel> {
    return apiClient.postJson<BuildingModel>(`/projects/${projectId}/model/generate`, params);
  }

  getModel(projectId: string): Promise<BuildingModel> {
    return apiClient.get<BuildingModel>(`/projects/${projectId}/model`);
  }
}
