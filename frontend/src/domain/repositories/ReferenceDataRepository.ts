import type { ConstructionTypeCatalog } from "@/domain/model/ConstructionTypeCatalog";

export interface ReferenceDataRepository {
  getConstructionTypes(): Promise<ConstructionTypeCatalog>;
}
