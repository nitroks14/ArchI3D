import { useRef, useState } from "react";

interface FileDropzoneProps {
  label: string;
  accept: string;
  /** Autorise la selection/le depot de plusieurs fichiers en une fois (ex: Photos, Factures). */
  multiple?: boolean;
  /** "environment" ouvre directement la camera arriere sur mobile (prise de vue in situ). */
  capture?: "environment" | "user";
  onFiles: (files: File[]) => void;
}

/**
 * Zone de depot de fichiers reutilisable (glisser-deposer + selection classique).
 *
 * Toute la zone (et pas uniquement le petit bouton natif du input file) est cliquable : plus
 * fiable inter-navigateurs et plus accessible sur mobile (cible tactile large, cf directive
 * "mobile-first"). Le input reel reste dans le DOM (visually-hidden via sr-only, pas "display:
 * none") pour garder un comportement natif complet (clavier, lecteurs d'ecran, `capture`).
 */
export function FileDropzone({ label, accept, multiple, capture, onFiles }: FileDropzoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const openPicker = () => inputRef.current?.click();

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`${label} - glisser-deposer ou choisir un fichier`}
      className={`flex cursor-pointer flex-wrap items-center gap-2 rounded-md border-2 border-dashed p-3 text-sm transition-colors ${
        dragging ? "border-primary bg-accent" : "border-input"
      }`}
      onClick={openPicker}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openPicker();
        }
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) onFiles(multiple ? files : files.slice(0, 1));
      }}
    >
      <span>
        {label} - glisser-deposer ou{" "}
        <span className="font-medium text-primary underline">choisir {multiple ? "des fichiers" : "un fichier"}</span>
      </span>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        capture={capture}
        className="sr-only"
        onClick={(e) => e.stopPropagation()}
        onChange={(e) => {
          const files = Array.from(e.target.files ?? []);
          if (files.length > 0) onFiles(files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
