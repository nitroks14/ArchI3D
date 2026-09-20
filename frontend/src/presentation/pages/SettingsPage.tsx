import { useState } from "react";

import type { User } from "@/domain/model/User";
import { authenticate } from "@/application/use-cases/Authenticate";
import { HttpAuthRepository } from "@/infrastructure/http/HttpAuthRepository";
import { ApiError } from "@/infrastructure/http/ApiClient";
import { Badge } from "@/presentation/components/ui/badge";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";

const authRepo = new HttpAuthRepository();
const authActions = authenticate(authRepo);

interface SettingsPageProps {
  user: User;
  onBack: () => void;
  onUserUpdated: (user: User) => void;
}

/**
 * Page "Parametres" : cle API Gemini personnelle de l'utilisateur, stockee chiffree cote backend
 * (cf backend/app/auth/crypto.py). Jamais affichee/renvoyee en clair une fois enregistree - seul
 * un apercu masque (ex: "AIza...xyz") est affiche.
 */
export function SettingsPage({ user, onBack, onUserUpdated }: SettingsPageProps) {
  const [apiKey, setApiKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSave = async () => {
    if (!apiKey.trim()) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await authActions.setGeminiApiKey(apiKey.trim());
      onUserUpdated(updated);
      setApiKey("");
      setSuccess("Cle enregistree.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue, voir la console.");
    } finally {
      setBusy(false);
    }
  };

  const handleClear = async () => {
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await authActions.clearGeminiApiKey();
      onUserUpdated(updated);
      setSuccess("Cle supprimee.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur inattendue, voir la console.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-5 p-4 sm:p-8">
      <header className="flex flex-wrap items-center gap-2">
        <Button variant="ghost" size="sm" onClick={onBack}>
          ← Retour
        </Button>
        <h1 className="text-2xl font-bold">Parametres</h1>
        {busy && <Badge variant="secondary">En cours...</Badge>}
        {error && <Badge variant="destructive">{error}</Badge>}
        {success && <Badge>{success}</Badge>}
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Cle API Gemini personnelle</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <p className="text-sm text-muted-foreground">
            Cree une cle gratuite sur{" "}
            <a
              href="https://ai.google.dev"
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              ai.google.dev
            </a>{" "}
            puis colle-la ci-dessous. Elle est chiffree avant stockage et n&apos;est jamais
            r&eacute;affich&eacute;e en clair.
          </p>

          <p className="text-sm">
            {user.geminiApiKeyConfigured
              ? `Cle actuelle : ${user.geminiApiKeyHint ?? "configuree"}`
              : "Aucune cle personnelle configuree (le serveur utilise la cle globale de dev, si definie)."}
          </p>

          <div className="space-y-1.5">
            <Label htmlFor="gemini-key">Nouvelle cle API Gemini</Label>
            <div className="flex flex-wrap gap-2">
              <Input
                id="gemini-key"
                type="password"
                autoComplete="off"
                className="w-full sm:w-80"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIza..."
              />
              <Button onClick={handleSave} disabled={!apiKey.trim() || busy}>
                Enregistrer
              </Button>
            </div>
          </div>

          {user.geminiApiKeyConfigured && (
            <Button variant="outline" onClick={handleClear} disabled={busy} className="self-start">
              Supprimer ma cle
            </Button>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
