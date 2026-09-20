import type { VisionAnalysisRepository } from "@/domain/repositories/VisionAnalysisRepository";
import type { PhotoAnalysis } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpVisionAnalysisRepository implements VisionAnalysisRepository {
  analyzePhoto(projectId: string, photoId: string): Promise<PhotoAnalysis> {
    return apiClient.postJson<PhotoAnalysis>(
      `/projects/${projectId}/photos/${photoId}/analyze`,
      {},
    );
  }
}
