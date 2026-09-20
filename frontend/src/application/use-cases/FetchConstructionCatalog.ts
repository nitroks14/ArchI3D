import type { ReferenceDataRepository } from "@/domain/repositories/ReferenceDataRepository";

export const fetchConstructionCatalog = (repo: ReferenceDataRepository) => () =>
  repo.getConstructionTypes();
