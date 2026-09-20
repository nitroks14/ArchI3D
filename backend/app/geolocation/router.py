import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.geolocation.service import GeocodingError, geocode_address, get_elevation
from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.shared.base import CamelModel
from app.shared.schemas import BuildingModel

router = APIRouter(prefix="/projects", tags=["geolocation"])


class GeocodeRequest(CamelModel):
    address: str


class LocationUpdateRequest(CamelModel):
    """Ajustement manuel (pin sur carte) et/ou reglage du compas d'orientation Nord."""

    latitude: float | None = None
    longitude: float | None = None
    altitude_m: float | None = None
    north_offset_deg: float | None = None


@router.post("/{project_id}/building/geocode", response_model=BuildingModel)
def geocode_building(
    payload: GeocodeRequest, state: ProjectState = Depends(get_owned_project_state)
) -> BuildingModel:
    building = state.building_model or BuildingModel(project_id=state.id)

    try:
        latitude, longitude = geocode_address(payload.address)
    except (GeocodingError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=400, detail=f"Geocodage impossible : {exc}") from exc

    building.address = payload.address
    building.latitude = latitude
    building.longitude = longitude
    building.altitude_m = get_elevation(latitude, longitude)

    state.building_model = building
    get_project_store().save(state)
    return building


@router.patch("/{project_id}/building/location", response_model=BuildingModel)
def update_building_location(
    payload: LocationUpdateRequest, state: ProjectState = Depends(get_owned_project_state)
) -> BuildingModel:
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Aucun batiment initialise pour ce projet")

    building = state.building_model
    if payload.latitude is not None:
        building.latitude = payload.latitude
    if payload.longitude is not None:
        building.longitude = payload.longitude
    if payload.altitude_m is not None:
        building.altitude_m = payload.altitude_m
    if payload.north_offset_deg is not None:
        building.north_offset_deg = payload.north_offset_deg

    get_project_store().save(state)
    return building
