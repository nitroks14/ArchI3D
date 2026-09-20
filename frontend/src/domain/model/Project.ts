import type { Annex } from "@/domain/model/Annex";
import type {
  AdditionalThermalMassLevel,
  BuildingModel,
  ThermalInertiaClass,
} from "@/domain/model/Building";
import type { UploadedFile } from "@/shared/types/common";

export interface PlanFile extends UploadedFile {
  floorLabel: string;
}

export interface PhotoFile extends UploadedFile {
  kind: "interior" | "exterior";
  roomId: string | null;
  analysis: PhotoAnalysis | null;
  /** Cap boussole (0-360, 0=Nord) releve au moment de la prise de vue - cf CameraCapture. */
  compassHeadingDeg: number | null;
}

export interface PhotoAnalysis {
  materials: string[];
  openingTypes: string[];
  apparentInsulationState: string;
  equipment: string[];
  suggestedRoomType: string | null;
  suggestedRoomName: string | null;
  suggestedCardinalOrientation: string | null;
  /**
   * Indice qualitatif pour la masse thermique complementaire (cheminee en pierre, chape beton
   * apparente...) - indicateur de confort d'ete, distinct de la classe d'inertie normee des
   * parois (non comptabilise par le calcul reglementaire RE2020/RT).
   */
  heavyThermalMassElementsDetected: string[];
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
  ownerId: string;
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
  /** Inertie des parois (normee RE2020/RT) - seul facteur de conformite reglementaire. */
  thermalInertiaClass: ThermalInertiaClass | null;
  /**
   * Masse thermique complementaire (mobilier) - indicateur QUALITATIF de confort d'ete / risque
   * de surchauffe, HORS calcul reglementaire. Toujours affiche separement de
   * thermalInertiaClass, jamais fusionne avec lui.
   */
  additionalThermalMassEstimate: AdditionalThermalMassLevel | null;
  assumptions: string[];
}
