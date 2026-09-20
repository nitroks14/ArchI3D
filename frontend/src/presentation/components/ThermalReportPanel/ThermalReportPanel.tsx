import type { ThermalReport } from "@/domain/model/Project";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";

interface ThermalReportPanelProps {
  report: ThermalReport | null;
  onCompute: () => void;
}

export function ThermalReportPanel({ report, onCompute }: ThermalReportPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>4. Rapport thermique (indicatif)</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <Button onClick={onCompute} className="self-start">
          Calculer / recalculer
        </Button>

        {report && (
          <div className="flex flex-col gap-4">
            <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <li className="rounded-md bg-secondary p-2 text-sm">
                <strong>Ubat approche</strong> : {report.ubatWPerM2k ?? "?"} W/m².K
              </li>
              <li className="rounded-md bg-secondary p-2 text-sm">
                <strong>Consommation estimee</strong> : {report.estimatedKwhPerM2PerYear ?? "?"} kWh/m²/an
              </li>
              <li className="rounded-md bg-secondary p-2 text-sm">
                <strong>Deperditions totales</strong> : {report.totalHeatLossCoefficientWPerK} W/K
              </li>
              <li className="rounded-md bg-secondary p-2 text-sm">
                <strong>Surface prise en compte</strong> : {report.floorAreaM2} m²
              </li>
            </ul>

            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="py-1 text-left">Poste</th>
                  <th className="py-1 text-left">W/K</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-1">Murs</td>
                  <td className="py-1">{report.breakdownWPerK.walls}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-1">Toiture</td>
                  <td className="py-1">{report.breakdownWPerK.roof}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-1">Plancher</td>
                  <td className="py-1">{report.breakdownWPerK.floor}</td>
                </tr>
                <tr className="border-b">
                  <td className="py-1">Vitrages</td>
                  <td className="py-1">{report.breakdownWPerK.windows}</td>
                </tr>
                <tr>
                  <td className="py-1">Ponts thermiques</td>
                  <td className="py-1">{report.breakdownWPerK.thermalBridges}</td>
                </tr>
              </tbody>
            </table>

            <details className="text-sm">
              <summary className="cursor-pointer font-medium">
                Hypotheses de calcul (valeurs indicatives - pas RE2020 certifie)
              </summary>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                {report.assumptions.map((assumption) => (
                  <li key={assumption}>{assumption}</li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
