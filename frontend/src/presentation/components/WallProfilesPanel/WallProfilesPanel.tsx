import type { WallAssemblyProfile } from "@/domain/model/WallProfile";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";

interface WallProfilesPanelProps {
  profiles: WallAssemblyProfile[];
  onApplyToUnset: (profileId: string, wallKind: string) => void;
}

const WALL_KIND_LABELS: Record<WallAssemblyProfile["applicableWallKind"], string> = {
  exterior: "murs exterieurs",
  interior: "murs interieurs",
  floor: "planchers",
  roof: "toitures",
};

/**
 * Bibliotheque de profils de paroi capitalises automatiquement (questionnaire, facture, vision)
 * au fil de la saisie. "Appliquer" est toujours une action EXPLICITE de l'utilisateur, jamais
 * automatique/silencieuse - et n'ecrase jamais une paroi deja renseignee individuellement.
 */
export function WallProfilesPanel({ profiles, onApplyToUnset }: WallProfilesPanelProps) {
  if (profiles.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profils de parois reutilisables</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <p className="text-sm text-muted-foreground">
          Compositions deja renseignees dans ce projet - reutilisables pour accelerer la saisie
          des elements similaires.
        </p>
        <ul className="flex flex-col gap-1.5">
          {profiles.map((profile) => (
            <li
              key={profile.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-secondary px-3 py-2 text-sm"
            >
              <span>
                {profile.label} - {WALL_KIND_LABELS[profile.applicableWallKind]} (utilise{" "}
                {profile.usageCount} fois)
              </span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onApplyToUnset(profile.id, profile.applicableWallKind)}
              >
                Appliquer aux {WALL_KIND_LABELS[profile.applicableWallKind]} non renseignes
              </Button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
