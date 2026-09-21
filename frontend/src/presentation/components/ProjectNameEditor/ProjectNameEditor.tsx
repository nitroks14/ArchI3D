import { useState } from "react";

import { Button } from "@/presentation/components/ui/button";
import { Input } from "@/presentation/components/ui/input";

interface ProjectNameEditorProps {
  name: string;
  busy?: boolean;
  onRename: (name: string) => void;
}

/**
 * Nom du projet affiche en haut de la page de detail - edition inline (clic sur le nom ou sur le
 * bouton "Renommer") avec sauvegarde via PATCH /projects/{id} (cf useProject.renameProject).
 */
export function ProjectNameEditor({ name, busy, onRename }: ProjectNameEditorProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(name);

  const startEditing = () => {
    setDraft(name);
    setEditing(true);
  };

  const commit = () => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== name) {
      onRename(trimmed);
    }
    setEditing(false);
  };

  const cancel = () => {
    setDraft(name);
    setEditing(false);
  };

  if (editing) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        <Input
          autoFocus
          className="w-56"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit();
            if (e.key === "Escape") cancel();
          }}
          disabled={busy}
        />
        <Button size="sm" onClick={commit} disabled={busy || !draft.trim()}>
          Enregistrer
        </Button>
        <Button size="sm" variant="ghost" onClick={cancel} disabled={busy}>
          Annuler
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <h1 className="text-2xl font-bold">{name}</h1>
      <Button size="sm" variant="outline" onClick={startEditing} disabled={busy}>
        Renommer
      </Button>
    </div>
  );
}
