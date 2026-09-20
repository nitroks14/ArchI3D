import type { ProjectRepository } from "@/domain/repositories/ProjectRepository";
import type { ProjectState } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpProjectRepository implements ProjectRepository {
  createProject(): Promise<ProjectState> {
    return apiClient.postJson<ProjectState>("/projects", {});
  }

  getProject(projectId: string): Promise<ProjectState> {
    return apiClient.get<ProjectState>(`/projects/${projectId}`);
  }

  listProjects(): Promise<ProjectState[]> {
    return apiClient.get<ProjectState[]>("/projects");
  }
}
