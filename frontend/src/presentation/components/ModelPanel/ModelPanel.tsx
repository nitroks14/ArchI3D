import { useState } from "react";

import type { PlanFile } from "@/domain/model/Project";
import type { GenerateModelParams } from "@/domain/repositories/ModelGenerationRepository";
import { ThreeViewer } from "@/presentation/components/ThreeViewer/ThreeViewer";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";

interface ModelPanelProps {
  plans: PlanFile[];
  glbUrl: string | null;
  onGenerate: (params: GenerateModelParams) => void;
}

export function ModelPanel({ plans, glbUrl, onGenerate }: ModelPanelProps) {
  const [metersPerPixel, setMetersPerPixel] = useState(0.02);
  const [ceilingHeight, setCeilingHeight] = useState(2.5);
  const [floorLevel, setFloorLevel] = useState(0);

  const latestPlan = plans[plans.length - 1];

  return (
    <Card>
      <CardHeader>
        <CardTitle>2. Modele 3D (heuristique plan {"->"} volume)</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {!latestPlan && <p className="text-sm text-muted-foreground">Uploade d&apos;abord un plan 2D.</p>}
        {latestPlan && (
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="meters-per-pixel">Echelle (m/pixel)</Label>
              <Input
                id="meters-per-pixel"
                type="number"
                step="0.001"
                className="w-28"
                value={metersPerPixel}
                onChange={(e) => setMetersPerPixel(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="ceiling-height">Hauteur sous plafond (m)</Label>
              <Input
                id="ceiling-height"
                type="number"
                step="0.1"
                className="w-28"
                value={ceilingHeight}
                onChange={(e) => setCeilingHeight(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="floor-level">Niveau (0=RDC, 1=etage 1, -1=sous-sol)</Label>
              <Input
                id="floor-level"
                type="number"
                className="w-28"
                value={floorLevel}
                onChange={(e) => setFloorLevel(Number(e.target.value))}
              />
            </div>
            <Button
              onClick={() =>
                onGenerate({
                  planId: latestPlan.id,
                  floorLabel: latestPlan.floorLabel,
                  floorLevel,
                  metersPerPixel,
                  defaultCeilingHeightM: ceilingHeight,
                })
              }
            >
              Generer le volume 3D
            </Button>
          </div>
        )}
        <ThreeViewer glbUrl={glbUrl} />
      </CardContent>
    </Card>
  );
}
