import type { PhotoAnalysis } from "@/domain/model/Project";

export interface VisionAnalysisRepository {
  analyzePhoto(projectId: string, photoId: string): Promise<PhotoAnalysis>;
}
