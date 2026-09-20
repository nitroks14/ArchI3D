import type { ProjectRepository } from "@/domain/repositories/ProjectRepository";

export const listProjects = (repo: ProjectRepository) => () => repo.listProjects();
