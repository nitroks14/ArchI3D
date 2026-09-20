import type { AnnexRepository } from "@/domain/repositories/AnnexRepository";

export const manageAnnexes = (repo: AnnexRepository) => ({
  list: (projectId: string) => repo.list(projectId),
  create: (projectId: string, input: Parameters<AnnexRepository["create"]>[1]) =>
    repo.create(projectId, input),
  remove: (projectId: string, annexId: string) => repo.remove(projectId, annexId),
});
