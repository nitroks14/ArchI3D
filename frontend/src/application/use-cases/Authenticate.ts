import type { AuthRepository } from "@/domain/repositories/AuthRepository";

export const authenticate = (repo: AuthRepository) => ({
  getCurrentUser: () => repo.getCurrentUser(),
  logout: () => repo.logout(),
  setGeminiApiKey: (apiKey: string) => repo.setGeminiApiKey(apiKey),
  clearGeminiApiKey: () => repo.clearGeminiApiKey(),
});
