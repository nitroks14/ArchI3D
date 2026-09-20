import { useState } from "react";

import type { Annex, AnnexType, CreateAnnexInput } from "@/domain/model/Annex";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/presentation/components/ui/select";

interface AnnexPanelProps {
  annexes: Annex[];
  onCreate: (input: CreateAnnexInput) => void;
  onRemove: (annexId: string) => void;
}

const ANNEX_TYPE_LABELS: Record<AnnexType, string> = {
  garden_shed: "Abri de jardin",
  garage: "Garage",
  outbuilding: "Dependance",
  other: "Autre",
};

const DEFAULT_INPUT: CreateAnnexInput = {
  type: "garden_shed",
  label: "Abri de jardin",
  offsetXM: 6,
  offsetYM: 0,
  widthM: 3,
  depthM: 3,
  heightM: 2.2,
  rotationDeg: 0,
  isConditioned: false,
};

/**
 * Agregat Annex (abri de jardin, garage, dependance...) - flux manuel V1 : l'utilisateur
 * positionne l'annexe sur le plan de masse (offsets en metres par rapport au batiment). La
 * detection automatique depuis l'image aerienne est un point d'integration vision IA pour V2
 * (meme principe que la detection des panneaux solaires - cf backend/app/vision_analysis).
 */
export function AnnexPanel({ annexes, onCreate, onRemove }: AnnexPanelProps) {
  const [input, setInput] = useState<CreateAnnexInput>(DEFAULT_INPUT);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Annexes (abris, garages, dependances)</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {annexes.length > 0 && (
          <ul className="flex flex-col gap-1.5">
            {annexes.map((annex) => (
              <li
                key={annex.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-secondary px-3 py-1.5 text-sm"
              >
                <span>
                  {annex.label} ({ANNEX_TYPE_LABELS[annex.type]}) - {annex.widthM}×{annex.depthM} m,
                  decalage ({annex.offsetXM}, {annex.offsetYM}) m
                </span>
                <Button variant="ghost" size="sm" onClick={() => onRemove(annex.id)}>
                  Supprimer
                </Button>
              </li>
            ))}
          </ul>
        )}

        <div className="flex flex-wrap items-end gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="annex-type">Type</Label>
            <Select
              value={input.type}
              onValueChange={(value) => setInput((prev) => ({ ...prev, type: value as AnnexType }))}
            >
              <SelectTrigger id="annex-type" className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(ANNEX_TYPE_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="annex-label">Nom</Label>
            <Input
              id="annex-label"
              className="w-40"
              value={input.label}
              onChange={(e) => setInput((prev) => ({ ...prev, label: e.target.value }))}
            />
          </div>

          {(
            [
              ["offsetXM", "Decalage X (m)"],
              ["offsetYM", "Decalage Y (m)"],
              ["widthM", "Largeur (m)"],
              ["depthM", "Profondeur (m)"],
              ["heightM", "Hauteur (m)"],
            ] as const
          ).map(([field, fieldLabel]) => (
            <div key={field} className="space-y-1.5">
              <Label htmlFor={`annex-${field}`}>{fieldLabel}</Label>
              <Input
                id={`annex-${field}`}
                type="number"
                step="0.1"
                className="w-24"
                value={input[field]}
                onChange={(e) =>
                  setInput((prev) => ({ ...prev, [field]: Number(e.target.value) }))
                }
              />
            </div>
          ))}

          <Button onClick={() => onCreate(input)}>Ajouter l&apos;annexe</Button>
        </div>
      </CardContent>
    </Card>
  );
}
