/**
 * Acces centralise aux variables d'environnement (import.meta.env), jamais de valeur
 * hardcodee ailleurs dans le code. Voir .env.example a la racine du frontend.
 */
export const env = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000",
} as const;
