import { useCallback, useEffect, useState } from "react";

import type { ProjectState } from "@/domain/model/Project";
import type { User } from "@/domain/model/User";
import { createProject } from "@/application/use-cases/CreateProject";
import { listProjects } from "@/application/use-cases/ListProjects";
import { HttpProjectRepository } from "@/infrastructure/http/HttpProjectRepository";
import { ApiError } from "@/infrastructure/http/ApiClient";
import { Badge } from "@/presentation/components/ui/badge";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";

const projectRepo = new HttpProjectRepository();

interface ProjectListPageProps {
  user: User;
  onOpenProject: (projectId: string) => void;
  onOpenSettings: () => void;
  onLogout: () => void;
}

/**
 * Liste uniquement les projets du proprietaire courant (GET /projects, filtre cote backend sur
 * ownerId) - aucun projet d'un autre utilisateur n'est jamais renvoye par l'API.
 */
export function ProjectListPage({ user, onOpenProject, onOpenSettings, onLogout }: ProjectListPageProps) {
  const [projects, setProjects] = useState<ProjectState[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      setProjects(await listProjects(projectRepo)());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue, voir la console.");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleCreate = async () => {
    setBusy(true);
    setError(null);
    try {
      const created = await createProject(projectRepo)();
      onOpenProject(created.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue, voir la console.");
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-5 p-4 sm:p-8">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold">ArchI3D</h1>
          <p className="text-sm text-muted-foreground">Connecte en tant que {user.displayName}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {busy && <Badge variant="secondary">En cours...</Badge>}
          {error && <Badge variant="destructive">{error}</Badge>}
          <Button variant="outline" onClick={onOpenSettings}>
            Parametres
          </Button>
          <Button variant="outline" onClick={onLogout}>
            Se deconnecter
          </Button>
        </div>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Mes projets</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Button onClick={handleCreate} className="self-start">
            Nouveau projet
          </Button>

          {projects && projects.length === 0 && (
            <p className="text-sm text-muted-foreground">Aucun projet pour l&apos;instant.</p>
          )}

          {projects && projects.length > 0 && (
            <ul className="flex flex-col gap-1.5">
              {projects.map((project) => (
                <li
                  key={project.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-secondary px-3 py-2 text-sm"
                >
                  <span>
                    {project.name || `Projet ${project.id}`} - cree le{" "}
                    {new Date(project.createdAt).toLocaleDateString("fr-FR")}
                  </span>
                  <Button size="sm" onClick={() => onOpenProject(project.id)}>
                    Ouvrir
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
