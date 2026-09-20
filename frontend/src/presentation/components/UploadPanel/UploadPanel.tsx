import { useState } from "react";

import type { ProjectState } from "@/domain/model/Project";

interface UploadPanelProps {
  project: ProjectState;
  onUploadAerial: (file: File) => void;
  onUploadPlan: (file: File, floorLabel: string) => void;
  onUploadPhoto: (file: File, kind: "interior" | "exterior") => void;
  onUploadInvoice: (file: File) => void;
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
}: UploadPanelProps) {
  const [floorLabel, setFloorLabel] = useState("RDC");
  const [photoKind, setPhotoKind] = useState<"interior" | "exterior">("interior");

  return (
    <section className="panel">
      <h2>1. Fichiers sources</h2>

      <DropZone label="Image aerienne du batiment" accept="image/*" onFile={onUploadAerial} />
      <p className="hint">{project.aerialImage ? "Image aerienne recue." : "Aucune image aerienne."}</p>

      <div className="row">
        <label htmlFor="floor-label">Etage du plan</label>
        <input
          id="floor-label"
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
      <p className="hint">{project.plans.length} plan(s) recu(s).</p>

      <div className="row">
        <label htmlFor="photo-kind">Type de photo</label>
        <select
          id="photo-kind"
          value={photoKind}
          onChange={(e) => setPhotoKind(e.target.value as "interior" | "exterior")}
        >
          <option value="interior">Interieure</option>
          <option value="exterior">Exterieure</option>
        </select>
      </div>
      <DropZone label="Photo" accept="image/*" onFile={(file) => onUploadPhoto(file, photoKind)} />
      <p className="hint">{project.photos.length} photo(s) recue(s).</p>

      <DropZone
        label="Facture / fiche technique materiau (PDF ou photo)"
        accept="image/*,application/pdf"
        onFile={onUploadInvoice}
      />
      <p className="hint">{project.invoices.length} facture(s) recue(s).</p>
    </section>
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
      className={`dropzone${dragging ? " dropzone--active" : ""}`}
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
      <label>
        {label} - glisser-deposer ou{" "}
        <input
          type="file"
          accept={accept}
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
