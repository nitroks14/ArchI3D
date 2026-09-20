import type { ProjectState } from "@/domain/model/Project";

export interface IngestionRepository {
  uploadAerialImage(projectId: string, file: File): Promise<ProjectState>;
  uploadPlan(projectId: string, file: File, floorLabel: string): Promise<ProjectState>;
  uploadPhoto(
    projectId: string,
    file: File,
    kind: "interior" | "exterior",
    roomId?: string,
  ): Promise<ProjectState>;
  uploadInvoice(projectId: string, file: File): Promise<ProjectState>;
}
