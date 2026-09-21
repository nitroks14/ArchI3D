import type { WallAssemblyProfile } from "@/domain/model/WallProfile";

export interface WallProfileRepository {
  list(projectId: string): Promise<WallAssemblyProfile[]>;
  applyToUnset(projectId: string, profileId: string, wallKind: string): Promise<number>;
}
