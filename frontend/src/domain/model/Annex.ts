/**
 * Agregat Annex (abri de jardin, garage, dependance...), distinct du Building principal.
 * Miroir de backend/app/annexes/schemas.py. Geometrie positionnee dans le meme repere local
 * (metres) que les pieces du batiment, pour apparaitre a cote de lui dans le viewer 3D.
 */
import type { ConstructionTypeId, Wall } from "@/domain/model/Building";

export type AnnexType = "garden_shed" | "garage" | "outbuilding" | "other";

export interface Annex {
  id: string;
  projectId: string;
  type: AnnexType;
  label: string;
  offsetXM: number;
  offsetYM: number;
  widthM: number;
  depthM: number;
  heightM: number;
  rotationDeg: number;
  isConditioned: boolean;
  constructionType: ConstructionTypeId;
  walls: Wall[];
  source: "user_input" | "vision_estimate";
}

export interface CreateAnnexInput {
  type: AnnexType;
  label: string;
  offsetXM: number;
  offsetYM: number;
  widthM: number;
  depthM: number;
  heightM: number;
  rotationDeg: number;
  isConditioned: boolean;
}
