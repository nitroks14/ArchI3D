import type { GeolocationRepository } from "@/domain/repositories/GeolocationRepository";
import type { BuildingModel } from "@/domain/model/Building";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpGeolocationRepository implements GeolocationRepository {
  geocodeAddress(projectId: string, address: string): Promise<BuildingModel> {
    return apiClient.postJson<BuildingModel>(`/projects/${projectId}/building/geocode`, { address });
  }

  updateLocation(
    projectId: string,
    payload: { latitude?: number; longitude?: number; altitudeM?: number; northOffsetDeg?: number },
  ): Promise<BuildingModel> {
    return apiClient.patchJson<BuildingModel>(`/projects/${projectId}/building/location`, payload);
  }
}
