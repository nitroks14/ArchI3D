import { env } from "@/shared/config/env";

/** Erreur HTTP enrichie du detail retourne par l'API (FastAPI renvoie {"detail": "..."}). */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      // reponse sans corps JSON exploitable, on garde le statusText
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`);
    return handleResponse<T>(response);
  },

  async postJson<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async patchJson<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async postForm<T>(path: string, form: FormData): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, { method: "POST", body: form });
    return handleResponse<T>(response);
  },
};
