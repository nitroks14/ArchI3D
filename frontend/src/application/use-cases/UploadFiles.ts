import type { IngestionRepository } from "@/domain/repositories/IngestionRepository";

/** Regroupe les 4 use-cases d'ingestion (upload direct, drag & drop cote UI) - meme repository. */
export const uploadFiles = (repo: IngestionRepository) => ({
  aerialImage: (projectId: string, file: File) => repo.uploadAerialImage(projectId, file),
  plan: (projectId: string, file: File, floorLabel: string) => repo.uploadPlan(projectId, file, floorLabel),
  photo: (projectId: string, file: File, kind: "interior" | "exterior") =>
    repo.uploadPhoto(projectId, file, kind),
  invoice: (projectId: string, file: File) => repo.uploadInvoice(projectId, file),
});
