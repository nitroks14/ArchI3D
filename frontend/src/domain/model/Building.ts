/**
 * Modele hierarchique du batiment, miroir des schemas Pydantic backend
 * (backend/app/shared/schemas.py). Maintenu manuellement en V1 - pas de generation
 * automatique de types depuis l'OpenAPI (cf README > compromis techniques).
 *
 * Building > Floor(s) > Room(s) > Wall(s) > Opening(s)
 *                               > Equipment(s)
 */
export type ConstructionTypeId =
  | "wood_frame"
  | "ite"
  | "monomur"
  | "parpaing_iti"
  | "brick"
  | "stone"
  | "unknown";

export type MaterialSource = "vision_estimate" | "invoice" | "user_input" | "default";

export type CardinalDirection = "N" | "NE" | "E" | "SE" | "S" | "SW" | "W" | "NW";

export interface Opening {
  id: string;
  type: "window" | "door";
  widthM: number;
  heightM: number;
  glazingType: string | null;
  uwValue: number | null;
}

export interface MaterialLayer {
  id: string;
  source: MaterialSource;
  materialRef: string | null;
  thicknessCm: number | null;
  rValue: number | null;
  productReference: string | null;
  invoiceId: string | null;
}

export interface Wall {
  id: string;
  kind: "exterior" | "interior" | "floor" | "roof";
  constructionType: ConstructionTypeId;
  lengthM: number | null;
  heightM: number | null;
  layers: MaterialLayer[];
  openings: Opening[];
  azimuthDeg: number | null;
  cardinalOrientation: CardinalDirection | null;
}

export interface SolarInstallation {
  id: string;
  source: "vision_estimate" | "user_input";
  areaM2: number | null;
  tiltDeg: number | null;
  cardinalOrientation: CardinalDirection | null;
  estimatedCapacityKwp: number | null;
  roofWallId: string | null;
}

export interface Equipment {
  id: string;
  type: "heating" | "ventilation" | "hot_water" | "other";
  label: string;
  source: "vision_estimate" | "user_input";
}

export interface RoomBoundingBox {
  x: number;
  y: number;
  widthM: number;
  depthM: number;
  heightM: number;
}

export interface Room {
  id: string;
  floorId: string;
  name: string;
  suggestedName: string | null;
  nameConfirmed: boolean;
  roomType: string | null;
  boundingBox: RoomBoundingBox;
  walls: Wall[];
  equipment: Equipment[];
  photoIds: string[];
}

export interface Floor {
  id: string;
  name: string;
  level: number;
  planId: string | null;
  rooms: Room[];
}

export interface BuildingModel {
  projectId: string;
  name: string;
  address: string | null;
  aerialImageId: string | null;
  floors: Floor[];
  generatedAt: string | null;
  glbUrl: string | null;
  latitude: number | null;
  longitude: number | null;
  altitudeM: number | null;
  northOffsetDeg: number;
  solarInstallations: SolarInstallation[];
}
