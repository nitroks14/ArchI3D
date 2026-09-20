import type { ReferenceDataRepository } from "@/domain/repositories/ReferenceDataRepository";
import type { ConstructionTypeCatalog } from "@/domain/model/ConstructionTypeCatalog";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpReferenceDataRepository implements ReferenceDataRepository {
  getConstructionTypes(): Promise<ConstructionTypeCatalog> {
    return apiClient.get<ConstructionTypeCatalog>("/reference/construction-types");
  }
}
