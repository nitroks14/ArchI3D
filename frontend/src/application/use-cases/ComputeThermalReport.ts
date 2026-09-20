import type { ThermalReportRepository } from "@/domain/repositories/ThermalReportRepository";

export const computeThermalReport = (repo: ThermalReportRepository) => (projectId: string) =>
  repo.getThermalReport(projectId);
