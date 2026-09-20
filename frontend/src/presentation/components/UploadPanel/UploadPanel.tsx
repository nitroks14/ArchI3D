import { useState } from "react";

import type { ProjectState } from "@/domain/model/Project";
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

interface UploadPanelProps {
  project: ProjectState;
  onUploadAerial: (file: File) => void;
  onUploadPlan: (file: File, floorLabel: string) => void;
  onUploadPhoto: (file: File, kind: "interior" | "exterior") => void;
  onUploadInvoice: (file: File) => void;
  onAnalyzeAerial: () => void;
}

/**
 * Upload direct (drag & drop ou selection classique) - methode d'ingestion retenue pour la V1.
 * Pas d'integration Google Drive en V1 (cf README > roadmap V2).
 */
export function UploadPanel({
  project,
  onUploadAerial,
  onUploadPlan,
  onUploadPhoto,
  onUploadInvoice,
  onAnalyzeAerial,
}: UploadPanelProps) {
  const [floorLabel, setFloorLabel] = useState("RDC");
  const [photoKind, setPhotoKind] = useState<"interior" | "exterior">("interior");

  return (
    <Card>
      <CardHeader>
        <CardTitle>1. Fichiers sources</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="space-y-1.5">
          <DropZone label="Image aerienne du batiment" accept="image/*" onFile={onUploadAerial} />
          <p className="text-sm text-muted-foreground">
            {project.aerialImage ? "Image aerienne recue." : "Aucune image aerienne."}
          </p>
          {project.aerialImage && (
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="outline" size="sm" onClick={onAnalyzeAerial}>
                Analyser l&apos;image aerienne (toiture / panneaux solaires)
              </Button>
              {project.aerialImageAnalysis && (
                <span className="text-sm text-muted-foreground">
                  {project.aerialImageAnalysis.solarPanelsDetected
                    ? `Panneaux solaires detectes (~${project.aerialImageAnalysis.solarPanelsAreaEstimateM2 ?? "?"} m²)`
                    : "Aucun panneau solaire detecte."}
                </span>
              )}
            </div>
          )}
        </div>

        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <Label htmlFor="floor-label">Etage du plan</Label>
            <Input
              id="floor-label"
              className="w-48"
              value={floorLabel}
              onChange={(e) => setFloorLabel(e.target.value)}
              placeholder="RDC, Etage 1, Combles..."
            />
          </div>
          <DropZone
            label={`Plan 2D (${floorLabel})`}
            accept="image/*"
            onFile={(file) => onUploadPlan(file, floorLabel)}
          />
          <p className="text-sm text-muted-foreground">{project.plans.length} plan(s) recu(s).</p>
        </div>

        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <Label htmlFor="photo-kind">Type de photo</Label>
            <Select value={photoKind} onValueChange={(value) => setPhotoKind(value as "interior" | "exterior")}>
              <SelectTrigger id="photo-kind" className="w-44">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="interior">Interieure</SelectItem>
                <SelectItem value="exterior">Exterieure</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DropZone label="Photo" accept="image/*" onFile={(file) => onUploadPhoto(file, photoKind)} />
          <p className="text-sm text-muted-foreground">{project.photos.length} photo(s) recue(s).</p>
        </div>

        <div className="space-y-1.5">
          <DropZone
            label="Facture / fiche technique materiau (PDF ou photo)"
            accept="image/*,application/pdf"
            onFile={onUploadInvoice}
          />
          <p className="text-sm text-muted-foreground">{project.invoices.length} facture(s) recue(s).</p>
        </div>
      </CardContent>
    </Card>
  );
}

function DropZone({
  label,
  accept,
  onFile,
}: {
  label: string;
  accept: string;
  onFile: (file: File) => void;
}) {
  const [dragging, setDragging] = useState(false);

  return (
    <div
      className={`rounded-md border-2 border-dashed p-3 text-sm transition-colors ${
        dragging ? "border-primary bg-accent" : "border-input"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) onFile(file);
      }}
    >
      <label className="flex flex-wrap items-center gap-2">
        <span>{label} - glisser-deposer ou</span>
        <input
          type="file"
          accept={accept}
          className="text-sm file:mr-2 file:rounded-md file:border-0 file:bg-secondary file:px-2 file:py-1 file:text-secondary-foreground"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFile(file);
            e.target.value = "";
          }}
        />
      </label>
    </div>
  );
}
