import { useCallback, useEffect, useMemo, useState } from "react";

import type { GenerateModelParams } from "@/domain/repositories/ModelGenerationRepository";
import type { ProjectState } from "@/domain/model/Project";
import type { QuestionnaireState } from "@/domain/model/Question";
import type { ConstructionTypeCatalog } from "@/domain/model/ConstructionTypeCatalog";
import { uploadFiles } from "@/application/use-cases/UploadFiles";
import { renameProject as renameProjectUseCase } from "@/application/use-cases/RenameProject";
import { analyzeAerialImage, analyzePhoto } from "@/application/use-cases/AnalyzePhoto";
import { generateBuildingModel } from "@/application/use-cases/GenerateBuildingModel";
import { manageMaterialInvoice } from "@/application/use-cases/ManageMaterialInvoice";
import { runQuestionnaireStep } from "@/application/use-cases/RunQuestionnaireStep";
import { computeThermalReport } from "@/application/use-cases/ComputeThermalReport";
import { fetchConstructionCatalog } from "@/application/use-cases/FetchConstructionCatalog";
import { manageBuildingLocation } from "@/application/use-cases/ManageBuildingLocation";
import { manageAnnexes } from "@/application/use-cases/ManageAnnexes";
import { manageWallProfiles } from "@/application/use-cases/ManageWallProfiles";
import type { CreateAnnexInput } from "@/domain/model/Annex";
import { HttpProjectRepository } from "@/infrastructure/http/HttpProjectRepository";
import { HttpWallProfileRepository } from "@/infrastructure/http/HttpWallProfileRepository";
import { HttpIngestionRepository } from "@/infrastructure/http/HttpIngestionRepository";
import { HttpVisionAnalysisRepository } from "@/infrastructure/http/HttpVisionAnalysisRepository";
import { HttpModelGenerationRepository } from "@/infrastructure/http/HttpModelGenerationRepository";
import { HttpMaterialInvoiceRepository } from "@/infrastructure/http/HttpMaterialInvoiceRepository";
import { HttpQuestionnaireRepository } from "@/infrastructure/http/HttpQuestionnaireRepository";
import { HttpThermalReportRepository } from "@/infrastructure/http/HttpThermalReportRepository";
import { HttpReferenceDataRepository } from "@/infrastructure/http/HttpReferenceDataRepository";
import { HttpGeolocationRepository } from "@/infrastructure/http/HttpGeolocationRepository";
import { HttpAnnexRepository } from "@/infrastructure/http/HttpAnnexRepository";
import { ApiError } from "@/infrastructure/http/ApiClient";

// Instanciation unique des repositories HTTP (pas de framework DI pour ce scaffold V1).
const projectRepo = new HttpProjectRepository();
const ingestionRepo = new HttpIngestionRepository();
const visionRepo = new HttpVisionAnalysisRepository();
const modelRepo = new HttpModelGenerationRepository();
const invoiceRepo = new HttpMaterialInvoiceRepository();
const questionnaireRepo = new HttpQuestionnaireRepository();
const thermalRepo = new HttpThermalReportRepository();
const referenceRepo = new HttpReferenceDataRepository();
const geolocationRepo = new HttpGeolocationRepository();
const annexRepo = new HttpAnnexRepository();
const wallProfileRepo = new HttpWallProfileRepository();

export function useProject(projectId: string) {
  const [project, setProject] = useState<ProjectState | null>(null);
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireState | null>(null);
  const [constructionCatalog, setConstructionCatalog] = useState<ConstructionTypeCatalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const uploads = useMemo(() => uploadFiles(ingestionRepo), []);
  const invoiceActions = useMemo(() => manageMaterialInvoice(invoiceRepo), []);
  const questionnaireActions = useMemo(() => runQuestionnaireStep(questionnaireRepo), []);
  const locationActions = useMemo(() => manageBuildingLocation(geolocationRepo), []);
  const annexActions = useMemo(() => manageAnnexes(annexRepo), []);
  const wallProfileActions = useMemo(() => manageWallProfiles(wallProfileRepo), []);

  const runSafely = useCallback(async <T,>(action: () => Promise<T>): Promise<T | undefined> => {
    setBusy(true);
    setError(null);
    try {
      return await action();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue, voir la console.");
      console.error(err);
      return undefined;
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    void runSafely(async () => {
      const loaded = await projectRepo.getProject(projectId);
      setProject(loaded);
      const catalog = await fetchConstructionCatalog(referenceRepo)();
      setConstructionCatalog(catalog);
      return loaded;
    });
  }, [projectId, runSafely]);

  const refreshProject = useCallback(
    (projectId: string) => runSafely(() => projectRepo.getProject(projectId).then(setProject)),
    [runSafely],
  );

  const refreshQuestionnaire = useCallback(
    (projectId: string) =>
      runSafely(() => questionnaireActions.next(projectId).then(setQuestionnaire)),
    [questionnaireActions, runSafely],
  );

  const uploadAerialImage = useCallback(
    (file: File) =>
      project && runSafely(() => uploads.aerialImage(project.id, file).then(setProject)),
    [project, uploads, runSafely],
  );

  const uploadPlan = useCallback(
    (file: File, floorLabel: string) =>
      project && runSafely(() => uploads.plan(project.id, file, floorLabel).then(setProject)),
    [project, uploads, runSafely],
  );

  const uploadPhoto = useCallback(
    (files: File[], kind: "interior" | "exterior", compassHeadingDeg?: number) =>
      project &&
      runSafely(() => uploads.photo(project.id, files, kind, compassHeadingDeg).then(setProject)),
    [project, uploads, runSafely],
  );

  const uploadInvoice = useCallback(
    (files: File[]) => project && runSafely(() => uploads.invoice(project.id, files).then(setProject)),
    [project, uploads, runSafely],
  );

  const analyzeProjectPhoto = useCallback(
    (photoId: string) =>
      project &&
      runSafely(async () => {
        await analyzePhoto(visionRepo)(project.id, photoId);
        await refreshProject(project.id);
      }),
    [project, refreshProject, runSafely],
  );

  const generateModel = useCallback(
    (params: GenerateModelParams) =>
      project &&
      runSafely(async () => {
        await generateBuildingModel(modelRepo)(project.id, params);
        await refreshProject(project.id);
      }),
    [project, refreshProject, runSafely],
  );

  const extractInvoice = useCallback(
    (invoiceId: string) =>
      project &&
      runSafely(async () => {
        await invoiceActions.extract(project.id, invoiceId);
        await refreshProject(project.id);
      }),
    [project, invoiceActions, refreshProject, runSafely],
  );

  const linkInvoice = useCallback(
    (invoiceId: string, roomId: string, wallId: string) =>
      project &&
      runSafely(async () => {
        await invoiceActions.link(project.id, invoiceId, roomId, wallId);
        await refreshProject(project.id);
      }),
    [project, invoiceActions, refreshProject, runSafely],
  );

  const answerQuestion = useCallback(
    (field: string, value: string) =>
      project &&
      runSafely(async () => {
        const next = await questionnaireActions.answer(project.id, field, value);
        setQuestionnaire(next);
        await refreshProject(project.id);
      }),
    [project, questionnaireActions, refreshProject, runSafely],
  );

  const getThermalReport = useCallback(
    () =>
      project &&
      runSafely(async () => {
        const report = await computeThermalReport(thermalRepo)(project.id);
        setProject((current) => (current ? { ...current, thermalReport: report } : current));
      }),
    [project, runSafely],
  );

  const geocodeAddress = useCallback(
    (address: string) =>
      project &&
      runSafely(async () => {
        await locationActions.geocode(project.id, address);
        await refreshProject(project.id);
      }),
    [project, locationActions, refreshProject, runSafely],
  );

  const updateNorthOffset = useCallback(
    (northOffsetDeg: number) =>
      project &&
      runSafely(async () => {
        await locationActions.updateLocation(project.id, { northOffsetDeg });
        await refreshProject(project.id);
      }),
    [project, locationActions, refreshProject, runSafely],
  );

  const analyzeAerial = useCallback(
    () =>
      project &&
      runSafely(async () => {
        await analyzeAerialImage(visionRepo)(project.id);
        await refreshProject(project.id);
      }),
    [project, refreshProject, runSafely],
  );

  const createAnnex = useCallback(
    (input: CreateAnnexInput) =>
      project &&
      runSafely(async () => {
        await annexActions.create(project.id, input);
        await refreshProject(project.id);
      }),
    [project, annexActions, refreshProject, runSafely],
  );

  const removeAnnex = useCallback(
    (annexId: string) =>
      project &&
      runSafely(async () => {
        await annexActions.remove(project.id, annexId);
        await refreshProject(project.id);
      }),
    [project, annexActions, refreshProject, runSafely],
  );

  const renameProject = useCallback(
    (name: string) =>
      project && runSafely(() => renameProjectUseCase(projectRepo)(project.id, name).then(setProject)),
    [project, runSafely],
  );

  const applyWallProfileToUnset = useCallback(
    (profileId: string, wallKind: string) =>
      project &&
      runSafely(async () => {
        await wallProfileActions.applyToUnset(project.id, profileId, wallKind);
        await refreshProject(project.id);
      }),
    [project, wallProfileActions, refreshProject, runSafely],
  );

  return {
    project,
    questionnaire,
    constructionCatalog,
    error,
    busy,
    refreshQuestionnaire: () => project && refreshQuestionnaire(project.id),
    uploadAerialImage,
    uploadPlan,
    uploadPhoto,
    uploadInvoice,
    renameProject,
    analyzeProjectPhoto,
    generateModel,
    extractInvoice,
    linkInvoice,
    answerQuestion,
    getThermalReport,
    geocodeAddress,
    updateNorthOffset,
    analyzeAerial,
    createAnnex,
    removeAnnex,
    applyWallProfileToUnset,
  };
}
