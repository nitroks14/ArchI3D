import { useState } from "react";

import type { BuildingModel } from "@/domain/model/Building";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import { Slider } from "@/presentation/components/ui/slider";

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
    <Card>
      <CardHeader>
        <CardTitle>Localisation &amp; orientation</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <Input
            className="w-64"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Adresse du batiment"
          />
          <Button onClick={() => onGeocode(address)} disabled={!address}>
            Geolocaliser
          </Button>
        </div>

        {building?.latitude != null && building.longitude != null && (
          <p className="text-sm text-muted-foreground">
            Lat {building.latitude.toFixed(5)}, Lon {building.longitude.toFixed(5)}
            {building.altitudeM != null ? `, altitude ${building.altitudeM.toFixed(0)} m` : ""}
          </p>
        )}

        <div className="space-y-2">
          <Label htmlFor="north-offset">Decalage Nord (degres, sens horaire)</Label>
          <div className="flex items-center gap-3">
            <Slider
              id="north-offset"
              className="max-w-xs"
              min={0}
              max={359}
              step={1}
              value={[building?.northOffsetDeg ?? 0]}
              onValueChange={(values) => onNorthOffsetChange(values[0] ?? 0)}
            />
            <span className="text-sm text-muted-foreground">{building?.northOffsetDeg ?? 0}°</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
