import type { ConstructionTypeId, MaterialLayer, MaterialSource } from "@/domain/model/Building";

/**
 * Profil de paroi reutilisable, capitalise automatiquement des qu'un mur/plancher/toiture recoit
 * une donnee exploitable (questionnaire, facture, vision) - propose ensuite en pre-remplissage
 * sur les elements similaires du meme projet. Miroir de backend/app/wall_profiles/schemas.py.
 */
export interface WallAssemblyProfile {
  id: string;
  label: string;
  applicableWallKind: "exterior" | "interior" | "floor" | "roof";
  constructionType: ConstructionTypeId;
  layers: MaterialLayer[];
  source: MaterialSource;
  usageCount: number;
  lastUsedAt: string;
}
