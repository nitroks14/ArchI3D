import type { GeolocationRepository } from "@/domain/repositories/GeolocationRepository";

export const manageBuildingLocation = (repo: GeolocationRepository) => ({
  geocode: (projectId: string, address: string) => repo.geocodeAddress(projectId, address),
  updateLocation: (projectId: string, payload: Parameters<GeolocationRepository["updateLocation"]>[1]) =>
    repo.updateLocation(projectId, payload),
});
