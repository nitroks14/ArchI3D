import { useState } from "react";

import type { PlanFile } from "@/domain/model/Project";
import type { GenerateModelParams } from "@/domain/repositories/ModelGenerationRepository";
import { ThreeViewer } from "@/presentation/components/ThreeViewer/ThreeViewer";

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
    <section className="panel">
      <h2>2. Modele 3D (heuristique plan {"->"} volume)</h2>
      {!latestPlan && <p className="hint">Uploade d&apos;abord un plan 2D.</p>}
      {latestPlan && (
        <div className="row">
          <label>
            Echelle (m/pixel)
            <input
              type="number"
              step="0.001"
              value={metersPerPixel}
              onChange={(e) => setMetersPerPixel(Number(e.target.value))}
            />
          </label>
          <label>
            Hauteur sous plafond (m)
            <input
              type="number"
              step="0.1"
              value={ceilingHeight}
              onChange={(e) => setCeilingHeight(Number(e.target.value))}
            />
          </label>
          <label>
            Niveau (0=RDC, 1=etage 1, -1=sous-sol)
            <input type="number" value={floorLevel} onChange={(e) => setFloorLevel(Number(e.target.value))} />
          </label>
          <button
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
          </button>
        </div>
      )}
      <ThreeViewer glbUrl={glbUrl} />
    </section>
  );
}
