import { useCallback, useEffect, useState } from "react";

import type { User } from "@/domain/model/User";
import { authenticate } from "@/application/use-cases/Authenticate";
import { HttpAuthRepository } from "@/infrastructure/http/HttpAuthRepository";
import { ApiError } from "@/infrastructure/http/ApiClient";
import { env } from "@/shared/config/env";

const authRepo = new HttpAuthRepository();
const authActions = authenticate(authRepo);

/**
 * Etat d'authentification global de l'app. Aucun token Google n'est jamais stocke cote client -
 * uniquement le cookie de session httpOnly pose par le backend (cf backend/app/auth), invisible
 * et inaccessible en JavaScript.
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const currentUser = await authActions.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setUser(null);
      } else {
        console.error(err);
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(() => {
    window.location.href = `${env.apiBaseUrl}/auth/google/login`;
  }, []);

  const logout = useCallback(async () => {
    await authActions.logout();
    setUser(null);
  }, []);

  return { user, loading, login, logout, refresh, setUser };
}
