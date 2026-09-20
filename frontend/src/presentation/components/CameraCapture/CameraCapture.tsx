import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/presentation/components/ui/button";

/**
 * Ecran camera integre (flux video live, camera arriere) avec relevé du cap boussole au moment
 * de la capture. Limitations documentées dans le README (precision boussole approximative,
 * support navigateur variable, HTTPS obligatoire) - non teste sur device reel dans ce sandbox.
 */

// Extension non-standard de DeviceOrientationEvent utilisee par iOS/Safari (cap boussole direct,
// deja exprime en degres 0-360 depuis le Nord - pas besoin de le recalculer depuis alpha).
interface IOSDeviceOrientationEvent extends DeviceOrientationEvent {
  webkitCompassHeading?: number;
}

// Extension non-standard de la classe DeviceOrientationEvent elle-meme (methode statique iOS
// 13+ obligatoire pour demander l'autorisation d'ecouter les evenements d'orientation).
interface IOSDeviceOrientationEventStatic {
  requestPermission?: () => Promise<"granted" | "denied">;
}

type CompassStatus = "unsupported" | "needs-permission" | "denied" | "active";

interface CameraCaptureProps {
  onCapture: (file: File, compassHeadingDeg: number | null) => void;
  onClose: () => void;
}

export function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [cameraError, setCameraError] = useState<string | null>(null);
  const [heading, setHeading] = useState<number | null>(null);
  const [compassStatus, setCompassStatus] = useState<CompassStatus>("unsupported");

  const handleOrientation = useCallback((event: Event) => {
    const orientationEvent = event as IOSDeviceOrientationEvent;
    if (typeof orientationEvent.webkitCompassHeading === "number") {
      setHeading(orientationEvent.webkitCompassHeading);
      return;
    }
    if (orientationEvent.absolute && typeof orientationEvent.alpha === "number") {
      // Approximation standard (non calibree, ne compense pas la rotation ecran) - cf README.
      setHeading((360 - orientationEvent.alpha) % 360);
    }
  }, []);

  // Demarrage du flux camera (arriere en priorite).
  useEffect(() => {
    let cancelled = false;

    async function start() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCameraError("Camera non disponible sur ce navigateur/appareil.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch {
        setCameraError("Acces a la camera refuse ou indisponible.");
      }
    }

    void start();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    };
  }, []);

  // Detection/ecoute de la boussole. Sur iOS 13+, une permission explicite (geste utilisateur)
  // est obligatoire - cf bouton "Activer la boussole" ci-dessous.
  useEffect(() => {
    if (typeof window === "undefined" || !("DeviceOrientationEvent" in window)) {
      setCompassStatus("unsupported");
      return;
    }

    const requestPermission = (
      DeviceOrientationEvent as unknown as IOSDeviceOrientationEventStatic
    ).requestPermission;

    if (typeof requestPermission === "function") {
      setCompassStatus("needs-permission");
      return;
    }

    setCompassStatus("active");
    window.addEventListener("deviceorientationabsolute", handleOrientation);
    window.addEventListener("deviceorientation", handleOrientation);
    return () => {
      window.removeEventListener("deviceorientationabsolute", handleOrientation);
      window.removeEventListener("deviceorientation", handleOrientation);
    };
  }, [handleOrientation]);

  const handleEnableCompass = async () => {
    const requestPermission = (
      DeviceOrientationEvent as unknown as IOSDeviceOrientationEventStatic
    ).requestPermission;
    if (!requestPermission) return;
    try {
      const result = await requestPermission();
      if (result === "granted") {
        setCompassStatus("active");
        window.addEventListener("deviceorientation", handleOrientation);
      } else {
        setCompassStatus("denied");
      }
    } catch {
      setCompassStatus("denied");
    }
  };

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], `photo-${Date.now()}.jpg`, { type: "image/jpeg" });
        onCapture(file, heading);
      },
      "image/jpeg",
      0.9,
    );
  };

  if (cameraError) {
    return (
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-4 bg-black p-6 text-center text-white">
        <p>{cameraError}</p>
        <p className="text-sm text-white/70">
          Utilise plutot le choix de fichier classique ci-dessous.
        </p>
        <Button variant="secondary" onClick={onClose}>
          Fermer
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-black">
      <video ref={videoRef} autoPlay playsInline muted className="min-h-0 flex-1 w-full object-cover" />

      <div className="absolute inset-x-0 top-0 flex items-center justify-between gap-2 p-3">
        <Button variant="secondary" size="sm" onClick={onClose}>
          Fermer
        </Button>

        <div className="rounded-md bg-black/50 px-3 py-1.5 text-sm text-white">
          {compassStatus === "active" && heading != null && `Cap : ${Math.round(heading)}°`}
          {compassStatus === "active" && heading == null && "Cap : en attente..."}
          {compassStatus === "needs-permission" && (
            <button onClick={() => void handleEnableCompass()} className="underline">
              Activer la boussole
            </button>
          )}
          {compassStatus === "denied" && "Boussole refusee"}
          {compassStatus === "unsupported" && "Boussole indisponible"}
        </div>
      </div>

      <div className="absolute inset-x-0 bottom-0 flex justify-center p-6">
        <button
          type="button"
          onClick={handleCapture}
          aria-label="Prendre la photo"
          className="h-16 w-16 rounded-full border-4 border-white bg-white/30 active:bg-white/50"
        />
      </div>
    </div>
  );
}
