import type { BuildingModel } from "@/domain/model/Building";

export interface GenerateModelParams {
  planId: string;
  floorLabel: string;
  floorLevel: number;
  metersPerPixel: number;
  defaultCeilingHeightM: number;
}

export interface ModelGenerationRepository {
  generateModel(projectId: string, params: GenerateModelParams): Promise<BuildingModel>;
  getModel(projectId: string): Promise<BuildingModel>;
}
