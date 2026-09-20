import type { IngestionRepository } from "@/domain/repositories/IngestionRepository";
import type { ProjectState } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpIngestionRepository implements IngestionRepository {
  uploadAerialImage(projectId: string, file: File): Promise<ProjectState> {
    const form = new FormData();
    form.append("file", file);
    return apiClient.postForm<ProjectState>(`/projects/${projectId}/aerial-image`, form);
  }

  uploadPlan(projectId: string, file: File, floorLabel: string): Promise<ProjectState> {
    const form = new FormData();
    form.append("file", file);
    form.append("floor_label", floorLabel);
    return apiClient.postForm<ProjectState>(`/projects/${projectId}/plans`, form);
  }

  uploadPhoto(
    projectId: string,
    file: File,
    kind: "interior" | "exterior",
    roomId?: string,
  ): Promise<ProjectState> {
    const form = new FormData();
    form.append("file", file);
    form.append("kind", kind);
    if (roomId) form.append("room_id", roomId);
    return apiClient.postForm<ProjectState>(`/projects/${projectId}/photos`, form);
  }

  uploadInvoice(projectId: string, file: File): Promise<ProjectState> {
    const form = new FormData();
    form.append("file", file);
    return apiClient.postForm<ProjectState>(`/projects/${projectId}/invoices`, form);
  }
}
