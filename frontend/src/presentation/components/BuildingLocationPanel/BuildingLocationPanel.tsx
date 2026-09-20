import { useState } from "react";

import type { BuildingModel } from "@/domain/model/Building";

interface BuildingLocationPanelProps {
  building: BuildingModel | null;
  onGeocode: (address: string) => void;
  onNorthOffsetChange: (northOffsetDeg: number) => void;
}

/**
 * Geolocalisation (geocodage Nominatim/OpenStreetMap + altitude Open-Meteo, cote backend) et
 * reglage du compas d'orientation Nord, utilise pour deriver l'orientation cardinale des
 * facades (apports solaires, ponts thermiques par facade - cf backend/app/shared/geo.py).
 */
export function BuildingLocationPanel({
  building,
  onGeocode,
  onNorthOffsetChange,
}: BuildingLocationPanelProps) {
  const [address, setAddress] = useState("");

  return (
    <section className="panel">
      <h2>Localisation &amp; orientation</h2>
      <div className="row">
        <input
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Adresse du batiment"
        />
        <button onClick={() => onGeocode(address)} disabled={!address}>
          Geolocaliser
        </button>
      </div>

      {building?.latitude != null && building.longitude != null && (
        <p className="hint">
          Lat {building.latitude.toFixed(5)}, Lon {building.longitude.toFixed(5)}
          {building.altitudeM != null ? `, altitude ${building.altitudeM.toFixed(0)} m` : ""}
        </p>
      )}

      <div className="row">
        <label htmlFor="north-offset">Decalage Nord (degres, sens horaire)</label>
        <input
          id="north-offset"
          type="range"
          min={0}
          max={359}
          value={building?.northOffsetDeg ?? 0}
          onChange={(e) => onNorthOffsetChange(Number(e.target.value))}
        />
        <span>{building?.northOffsetDeg ?? 0}°</span>
      </div>
    </section>
  );
}
