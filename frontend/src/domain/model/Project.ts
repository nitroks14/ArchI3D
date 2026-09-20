import type { Annex } from "@/domain/model/Annex";
import type { BuildingModel } from "@/domain/model/Building";
import type { UploadedFile } from "@/shared/types/common";

export interface PlanFile extends UploadedFile {
  floorLabel: string;
}

export interface PhotoFile extends UploadedFile {
  kind: "interior" | "exterior";
  roomId: string | null;
  analysis: PhotoAnalysis | null;
}

export interface PhotoAnalysis {
  materials: string[];
  openingTypes: string[];
  apparentInsulationState: string;
  equipment: string[];
  suggestedRoomType: string | null;
  suggestedRoomName: string | null;
  confidence: string;
}

export interface ExtractedMaterial {
  material: string | null;
  productReference: string | null;
  thicknessCm: number | null;
  rValue: number | null;
  quantity: string | null;
  warning?: string;
}

export interface MaterialInvoiceFile extends UploadedFile {
  ocrText: string;
  extracted: ExtractedMaterial | null;
  linkedRoomId: string | null;
  linkedWallId: string | null;
}

export interface AerialImageAnalysis {
  roofShape: string | null;
  solarPanelsDetected: boolean;
  solarPanelsAreaEstimateM2: number | null;
  solarPanelsLocationHint: string | null;
  confidence: string;
}

export interface ProjectState {
  id: string;
  createdAt: string;
  aerialImage: UploadedFile | null;
  plans: PlanFile[];
  photos: PhotoFile[];
  invoices: MaterialInvoiceFile[];
  buildingModel: BuildingModel | null;
  annexes: Annex[];
  questionnaireAnswers: Record<string, string>;
  thermalReport: ThermalReport | null;
  aerialImageAnalysis: AerialImageAnalysis | null;
}

export interface ThermalReportBreakdown {
  walls: number;
  roof: number;
  floor: number;
  windows: number;
  thermalBridges: number;
}

export interface ThermalReport {
  floorAreaM2: number;
  totalHeatLossCoefficientWPerK: number;
  breakdownWPerK: ThermalReportBreakdown;
  ubatWPerM2k: number | null;
  djuUsed: number;
  djuSource: string;
  estimatedAnnualHeatingKwh: number;
  estimatedKwhPerM2PerYear: number | null;
  assumptions: string[];
}
