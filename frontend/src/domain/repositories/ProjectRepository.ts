import type { ProjectState } from "@/domain/model/Project";

export interface ProjectRepository {
  createProject(): Promise<ProjectState>;
  getProject(projectId: string): Promise<ProjectState>;
  listProjects(): Promise<ProjectState[]>;
}
