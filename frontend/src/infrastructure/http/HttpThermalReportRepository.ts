import type { ThermalReportRepository } from "@/domain/repositories/ThermalReportRepository";
import type { ThermalReport } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpThermalReportRepository implements ThermalReportRepository {
  getThermalReport(projectId: string): Promise<ThermalReport> {
    return apiClient.get<ThermalReport>(`/projects/${projectId}/thermal-report`);
  }
}
