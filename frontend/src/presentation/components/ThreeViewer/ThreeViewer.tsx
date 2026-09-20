import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Grid, OrbitControls, useGLTF } from "@react-three/drei";

interface ThreeViewerProps {
  glbUrl: string | null;
}

/**
 * Viewer 3D du volume simplifie (boites par piece) genere par le backend a partir du plan 2D.
 * Rendu volontairement schematique (pas de photorealisme) - coherent avec l'approche hybride
 * structuree retenue pour la reconstruction 3D (cf README).
 */
export function ThreeViewer({ glbUrl }: ThreeViewerProps) {
  if (!glbUrl) {
    return (
      <div className="flex h-[420px] w-full items-center justify-center rounded-md border border-dashed text-center text-sm text-muted-foreground">
        Aucun modele genere pour l&apos;instant - uploade un plan puis lance la generation.
      </div>
    );
  }

  return (
    <div className="h-[420px] w-full overflow-hidden rounded-md bg-neutral-900">
      <Canvas camera={{ position: [12, 12, 12], fov: 45 }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 15, 5]} intensity={0.8} />
        <Suspense fallback={null}>
          <BuildingModelMesh url={glbUrl} />
        </Suspense>
        <Grid args={[50, 50]} cellColor="#444" sectionColor="#666" />
        <OrbitControls />
      </Canvas>
    </div>
  );
}

function BuildingModelMesh({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}
