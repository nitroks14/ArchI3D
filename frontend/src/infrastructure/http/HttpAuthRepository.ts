import type { AuthRepository } from "@/domain/repositories/AuthRepository";
import type { User } from "@/domain/model/User";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpAuthRepository implements AuthRepository {
  getCurrentUser(): Promise<User> {
    return apiClient.get<User>("/auth/me");
  }

  async logout(): Promise<void> {
    await apiClient.postEmpty("/auth/logout");
  }

  setGeminiApiKey(apiKey: string): Promise<User> {
    return apiClient.putJson<User>("/auth/me/gemini-key", { apiKey });
  }

  async clearGeminiApiKey(): Promise<User> {
    return apiClient.deleteRequest<User>("/auth/me/gemini-key");
  }
}
