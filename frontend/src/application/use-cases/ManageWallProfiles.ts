import type { WallProfileRepository } from "@/domain/repositories/WallProfileRepository";

export const manageWallProfiles = (repo: WallProfileRepository) => ({
  list: (projectId: string) => repo.list(projectId),
  applyToUnset: (projectId: string, profileId: string, wallKind: string) =>
    repo.applyToUnset(projectId, profileId, wallKind),
});
