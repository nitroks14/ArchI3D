import type { BuildingModel } from "@/domain/model/Building";

export interface GeolocationRepository {
  geocodeAddress(projectId: string, address: string): Promise<BuildingModel>;
  updateLocation(
    projectId: string,
    payload: { latitude?: number; longitude?: number; altitudeM?: number; northOffsetDeg?: number },
  ): Promise<BuildingModel>;
}
