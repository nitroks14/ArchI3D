import type { WallProfileRepository } from "@/domain/repositories/WallProfileRepository";
import type { WallAssemblyProfile } from "@/domain/model/WallProfile";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpWallProfileRepository implements WallProfileRepository {
  list(projectId: string): Promise<WallAssemblyProfile[]> {
    return apiClient.get<WallAssemblyProfile[]>(`/projects/${projectId}/wall-profiles`);
  }

  async applyToUnset(projectId: string, profileId: string, wallKind: string): Promise<number> {
    const response = await apiClient.postJson<{ appliedCount: number }>(
      `/projects/${projectId}/wall-profiles/${profileId}/apply-to-unset`,
      { wallKind },
    );
    return response.appliedCount;
  }
}
