import type { ThermalReport } from "@/domain/model/Project";

export interface ThermalReportRepository {
  getThermalReport(projectId: string): Promise<ThermalReport>;
}
