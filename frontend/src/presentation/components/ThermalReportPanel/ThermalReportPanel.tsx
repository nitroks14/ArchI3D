import type { ThermalReport } from "@/domain/model/Project";

interface ThermalReportPanelProps {
  report: ThermalReport | null;
  onCompute: () => void;
}

export function ThermalReportPanel({ report, onCompute }: ThermalReportPanelProps) {
  return (
    <section className="panel">
      <h2>4. Rapport thermique (indicatif)</h2>
      <button onClick={onCompute}>Calculer / recalculer</button>

      {report && (
        <div className="thermal-report">
          <ul className="metrics">
            <li>
              <strong>Ubat approche</strong> : {report.ubatWPerM2k ?? "?"} W/m².K
            </li>
            <li>
              <strong>Consommation estimee</strong> : {report.estimatedKwhPerM2PerYear ?? "?"} kWh/m²/an
            </li>
            <li>
              <strong>Deperditions totales</strong> : {report.totalHeatLossCoefficientWPerK} W/K
            </li>
            <li>
              <strong>Surface prise en compte</strong> : {report.floorAreaM2} m²
            </li>
          </ul>

          <table>
            <thead>
              <tr>
                <th>Poste</th>
                <th>W/K</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Murs</td>
                <td>{report.breakdownWPerK.walls}</td>
              </tr>
              <tr>
                <td>Toiture</td>
                <td>{report.breakdownWPerK.roof}</td>
              </tr>
              <tr>
                <td>Plancher</td>
                <td>{report.breakdownWPerK.floor}</td>
              </tr>
              <tr>
                <td>Vitrages</td>
                <td>{report.breakdownWPerK.windows}</td>
              </tr>
              <tr>
                <td>Ponts thermiques</td>
                <td>{report.breakdownWPerK.thermalBridges}</td>
              </tr>
            </tbody>
          </table>

          <details>
            <summary>Hypotheses de calcul (valeurs indicatives - pas RE2020 certifie)</summary>
            <ul>
              {report.assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </section>
  );
}
