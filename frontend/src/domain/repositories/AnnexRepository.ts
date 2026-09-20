import type { Annex, CreateAnnexInput } from "@/domain/model/Annex";

export interface AnnexRepository {
  list(projectId: string): Promise<Annex[]>;
  create(projectId: string, input: CreateAnnexInput): Promise<Annex>;
  update(projectId: string, annexId: string, input: Partial<CreateAnnexInput>): Promise<Annex>;
  remove(projectId: string, annexId: string): Promise<void>;
}
