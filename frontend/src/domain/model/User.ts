export interface User {
  id: string;
  email: string;
  displayName: string;
  createdAt: string;
  geminiApiKeyConfigured: boolean;
  geminiApiKeyHint: string | null;
}
