import type { User } from "@/domain/model/User";

export interface AuthRepository {
  getCurrentUser(): Promise<User>;
  logout(): Promise<void>;
  setGeminiApiKey(apiKey: string): Promise<User>;
  clearGeminiApiKey(): Promise<User>;
}
