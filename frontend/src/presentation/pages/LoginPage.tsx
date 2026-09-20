import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";

interface LoginPageProps {
  onLogin: () => void;
}

/**
 * Ecran non-authentifie qui bloque l'acces au reste de l'app (photos, plans, factures sont des
 * donnees sensibles - cf exigence controle d'acces). La connexion redirige vers le backend
 * (/auth/google/login), qui gere lui-meme tout le flow OAuth aupres de Google.
 */
export function LoginPage({ onLogin }: LoginPageProps) {
  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>ArchI3D</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            Connecte-toi pour acceder a tes projets (photos, plans et factures sont des donnees
            privees, visibles uniquement par toi).
          </p>
          <Button onClick={onLogin}>Se connecter avec Google</Button>
        </CardContent>
      </Card>
    </main>
  );
}
