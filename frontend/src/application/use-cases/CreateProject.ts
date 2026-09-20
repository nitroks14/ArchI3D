import type { ProjectRepository } from "@/domain/repositories/ProjectRepository";

export const createProject = (repo: ProjectRepository) => () => repo.createProject();
