import type { VisionAnalysisRepository } from "@/domain/repositories/VisionAnalysisRepository";

export const analyzePhoto = (repo: VisionAnalysisRepository) => (projectId: string, photoId: string) =>
  repo.analyzePhoto(projectId, photoId);

export const analyzeAerialImage = (repo: VisionAnalysisRepository) => (projectId: string) =>
  repo.analyzeAerialImage(projectId);
