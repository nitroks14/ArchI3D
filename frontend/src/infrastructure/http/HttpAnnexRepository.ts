import type { AnnexRepository } from "@/domain/repositories/AnnexRepository";
import type { Annex, CreateAnnexInput } from "@/domain/model/Annex";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpAnnexRepository implements AnnexRepository {
  list(projectId: string): Promise<Annex[]> {
    return apiClient.get<Annex[]>(`/projects/${projectId}/annexes`);
  }

  create(projectId: string, input: CreateAnnexInput): Promise<Annex> {
    return apiClient.postJson<Annex>(`/projects/${projectId}/annexes`, input);
  }

  update(projectId: string, annexId: string, input: Partial<CreateAnnexInput>): Promise<Annex> {
    return apiClient.patchJson<Annex>(`/projects/${projectId}/annexes/${annexId}`, input);
  }

  async remove(projectId: string, annexId: string): Promise<void> {
    await apiClient.deleteRequest(`/projects/${projectId}/annexes/${annexId}`);
  }
}
