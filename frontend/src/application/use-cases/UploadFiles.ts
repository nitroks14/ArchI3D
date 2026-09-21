import type { IngestionRepository } from "@/domain/repositories/IngestionRepository";
import type { ProjectState } from "@/domain/model/Project";

/**
 * Regroupe les 4 use-cases d'ingestion (upload direct, drag & drop cote UI) - meme repository.
 *
 * Photo et Facture acceptent plusieurs fichiers en une fois (cf UploadPanel > multiple) : l'API
 * backend ne gerant qu'un fichier par requete, on boucle sequentiellement (un appel par fichier,
 * chacun renvoyant l'etat projet a jour) et on retourne l'etat final une fois tous les fichiers
 * envoyes.
 */
export const uploadFiles = (repo: IngestionRepository) => ({
  aerialImage: (projectId: string, file: File) => repo.uploadAerialImage(projectId, file),
  plan: (projectId: string, file: File, floorLabel: string) => repo.uploadPlan(projectId, file, floorLabel),
  photo: async (
    projectId: string,
    files: File[],
    kind: "interior" | "exterior",
    compassHeadingDeg?: number,
  ): Promise<ProjectState> => {
    let state: ProjectState | undefined;
    for (const file of files) {
      state = await repo.uploadPhoto(projectId, file, kind, undefined, compassHeadingDeg);
    }
    if (!state) throw new Error("Aucun fichier a uploader");
    return state;
  },
  invoice: async (projectId: string, files: File[]): Promise<ProjectState> => {
    let state: ProjectState | undefined;
    for (const file of files) {
      state = await repo.uploadInvoice(projectId, file);
    }
    if (!state) throw new Error("Aucun fichier a uploader");
    return state;
  },
});
