import { useState } from "react";

import type { ProjectState } from "@/domain/model/Project";
import { CameraCapture } from "@/presentation/components/CameraCapture/CameraCapture";
import { FileDropzone } from "@/presentation/components/FileDropzone/FileDropzone";
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

// Detection ponctuelle (au chargement du module) : disponible sur la quasi-totalite des
// navigateurs mobiles modernes en contexte HTTPS, absent sur les navigateurs plus anciens ou en
// HTTP. Repli propre garanti : le DropZone classique (input file) reste toujours disponible.
const CAMERA_SUPPORTED =
  typeof navigator !== "undefined" && typeof navigator.mediaDevices?.getUserMedia === "function";

interface UploadPanelProps {
  project: ProjectState;
  onUploadAerial: (file: File) => void;
  onUploadPlan: (file: File, floorLabel: string) => void;
  onUploadPhoto: (files: File[], kind: "interior" | "exterior", compassHeadingDeg?: number) => void;
  onUploadInvoice: (files: File[]) => void;
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
  const [showCamera, setShowCamera] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle>1. Fichiers sources</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="space-y-1.5">
          <FileDropzone
            label="Image aerienne du batiment"
            accept="image/*"
            onFiles={(files) => {
              const [file] = files;
              if (file) onUploadAerial(file);
            }}
          />
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
          <FileDropzone
            label={`Plan 2D (${floorLabel})`}
            accept="image/*"
            onFiles={(files) => {
              const [file] = files;
              if (file) onUploadPlan(file, floorLabel);
            }}
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
          {CAMERA_SUPPORTED && (
            <Button type="button" variant="outline" size="sm" onClick={() => setShowCamera(true)}>
              Prendre une photo (camera + boussole)
            </Button>
          )}
          <FileDropzone
            label="Photo(s)"
            accept="image/*"
            capture="environment"
            multiple
            onFiles={(files) => onUploadPhoto(files, photoKind)}
          />
          <p className="text-sm text-muted-foreground">{project.photos.length} photo(s) recue(s).</p>
        </div>

        <div className="space-y-1.5">
          <FileDropzone
            label="Facture(s) / fiche(s) technique(s) materiau (PDF ou photo)"
            accept="image/*,application/pdf"
            multiple
            onFiles={onUploadInvoice}
          />
          <p className="text-sm text-muted-foreground">{project.invoices.length} facture(s) recue(s).</p>
        </div>
      </CardContent>

      {showCamera && (
        <CameraCapture
          onCapture={(file, compassHeadingDeg) => {
            onUploadPhoto([file], photoKind, compassHeadingDeg ?? undefined);
            setShowCamera(false);
          }}
          onClose={() => setShowCamera(false)}
        />
      )}
    </Card>
  );
}
