export interface ConstructionTypeEntry {
  label: string;
  description: string;
  insulationPosition: "ITE" | "ITI" | "none" | "integrated";
  defaultWallUValue: number;
  imageAsset: string;
}

export type ConstructionTypeCatalog = Record<string, ConstructionTypeEntry>;
