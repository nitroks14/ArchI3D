import type { VisionAnalysisRepository } from "@/domain/repositories/VisionAnalysisRepository";
import type { AerialImageAnalysis, PhotoAnalysis } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpVisionAnalysisRepository implements VisionAnalysisRepository {
  analyzePhoto(projectId: string, photoId: string): Promise<PhotoAnalysis> {
    return apiClient.postJson<PhotoAnalysis>(
      `/projects/${projectId}/photos/${photoId}/analyze`,
      {},
    );
  }

  analyzeAerialImage(projectId: string): Promise<AerialImageAnalysis> {
    return apiClient.postJson<AerialImageAnalysis>(
      `/projects/${projectId}/aerial-image/analyze`,
      {},
    );
  }
}
