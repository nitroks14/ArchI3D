import type { ProjectRepository } from "@/domain/repositories/ProjectRepository";

export const renameProject = (repo: ProjectRepository) => (projectId: string, name: string) =>
  repo.renameProject(projectId, name);
