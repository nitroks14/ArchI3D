import { useState } from "react";

import { useAuth } from "@/presentation/hooks/useAuth";
import { LoginPage } from "@/presentation/pages/LoginPage";
import { ProjectListPage } from "@/presentation/pages/ProjectListPage";
import { ProjectPage } from "@/presentation/pages/ProjectPage";
import { SettingsPage } from "@/presentation/pages/SettingsPage";

export function App() {
  const { user, loading, login, logout, setUser } = useAuth();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  if (loading) {
    return <p className="p-8 text-center text-muted-foreground">Chargement...</p>;
  }

  if (!user) {
    return <LoginPage onLogin={login} />;
  }

  if (showSettings) {
    return (
      <SettingsPage user={user} onBack={() => setShowSettings(false)} onUserUpdated={setUser} />
    );
  }

  if (selectedProjectId) {
    return <ProjectPage projectId={selectedProjectId} onBack={() => setSelectedProjectId(null)} />;
  }

  return (
    <ProjectListPage
      user={user}
      onOpenProject={setSelectedProjectId}
      onOpenSettings={() => setShowSettings(true)}
      onLogout={() => void logout()}
    />
  );
}
