import { useProject } from "@/presentation/hooks/useProject";
import { UploadPanel } from "@/presentation/components/UploadPanel/UploadPanel";
import { ModelPanel } from "@/presentation/components/ModelPanel/ModelPanel";
import { BuildingLocationPanel } from "@/presentation/components/BuildingLocationPanel/BuildingLocationPanel";
import { QuestionnairePanel } from "@/presentation/components/QuestionnairePanel/QuestionnairePanel";
import { ThermalReportPanel } from "@/presentation/components/ThermalReportPanel/ThermalReportPanel";

export function ProjectPage() {
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
  } = useProject();

  if (!project) {
    return <p className="loading">Initialisation du projet...</p>;
  }

  return (
    <main className="project-page">
      <header>
        <h1>ArchI3D</h1>
        <p className="hint">Projet {project.id}</p>
        {busy && <span className="badge">En cours...</span>}
        {error && <span className="badge badge--error">{error}</span>}
      </header>

      <UploadPanel
        project={project}
        onUploadAerial={(file) => uploadAerialImage(file)}
        onUploadPlan={(file, floorLabel) => uploadPlan(file, floorLabel)}
        onUploadPhoto={(file, kind) => uploadPhoto(file, kind)}
        onUploadInvoice={(file) => uploadInvoice(file)}
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

      <QuestionnairePanel
        questionnaire={questionnaire}
        onLoadNext={() => refreshQuestionnaire()}
        onAnswer={(field, value) => answerQuestion(field, value)}
      />

      <ThermalReportPanel report={project.thermalReport} onCompute={() => getThermalReport()} />
    </main>
  );
}
