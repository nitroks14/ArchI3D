import { useProject } from "@/presentation/hooks/useProject";
import { UploadPanel } from "@/presentation/components/UploadPanel/UploadPanel";
import { ModelPanel } from "@/presentation/components/ModelPanel/ModelPanel";
import { BuildingLocationPanel } from "@/presentation/components/BuildingLocationPanel/BuildingLocationPanel";
import { QuestionnairePanel } from "@/presentation/components/QuestionnairePanel/QuestionnairePanel";
import { ThermalReportPanel } from "@/presentation/components/ThermalReportPanel/ThermalReportPanel";
import { AnnexPanel } from "@/presentation/components/AnnexPanel/AnnexPanel";
import { Badge } from "@/presentation/components/ui/badge";
import { Button } from "@/presentation/components/ui/button";

interface ProjectPageProps {
  projectId: string;
  onBack: () => void;
}

export function ProjectPage({ projectId, onBack }: ProjectPageProps) {
  const {
    project,
    questionnaire,
    error,
    busy,
    refreshQuestionnaire,
    uploadAerialImage,
    uploadPlan,
    uploadPhoto,
    uploadInvoice,
    generateModel,
    answerQuestion,
    getThermalReport,
    geocodeAddress,
    updateNorthOffset,
    analyzeAerial,
    createAnnex,
    removeAnnex,
  } = useProject(projectId);

  if (!project) {
    return <p className="p-8 text-center text-muted-foreground">Chargement du projet...</p>;
  }

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-5 p-4 sm:p-8">
      <header className="flex flex-wrap items-center gap-2">
        <Button variant="ghost" size="sm" onClick={onBack}>
          ← Mes projets
        </Button>
        <h1 className="text-2xl font-bold">ArchI3D</h1>
        <p className="text-sm text-muted-foreground">Projet {project.id}</p>
        {busy && <Badge variant="secondary">En cours...</Badge>}
        {error && <Badge variant="destructive">{error}</Badge>}
      </header>

      <UploadPanel
        project={project}
        onUploadAerial={(file) => uploadAerialImage(file)}
        onUploadPlan={(file, floorLabel) => uploadPlan(file, floorLabel)}
        onUploadPhoto={(file, kind) => uploadPhoto(file, kind)}
        onUploadInvoice={(file) => uploadInvoice(file)}
        onAnalyzeAerial={() => analyzeAerial()}
      />

      <BuildingLocationPanel
        building={project.buildingModel}
        onGeocode={(address) => geocodeAddress(address)}
        onNorthOffsetChange={(deg) => updateNorthOffset(deg)}
      />

      <ModelPanel
        plans={project.plans}
        glbUrl={project.buildingModel?.glbUrl ?? null}
        onGenerate={(params) => generateModel(params)}
      />

      <AnnexPanel
        annexes={project.annexes}
        onCreate={(input) => createAnnex(input)}
        onRemove={(annexId) => removeAnnex(annexId)}
      />

      <QuestionnairePanel
        questionnaire={questionnaire}
        onLoadNext={() => refreshQuestionnaire()}
        onAnswer={(field, value) => answerQuestion(field, value)}
      />

      <ThermalReportPanel report={project.thermalReport} onCompute={() => getThermalReport()} />
    </main>
  );
}
