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

// "include" : necessaire pour que le cookie de session httpOnly (cf backend/app/auth) soit
// envoye/recu meme lorsque frontend et backend sont sur des origines differentes (dev local
// ports differents, prod GitHub Pages + backend separe - cross-site, cf README > Authentification).
const CREDENTIALS: RequestCredentials = "include";

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, { credentials: CREDENTIALS });
    return handleResponse<T>(response);
  },

  async postJson<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: CREDENTIALS,
    });
    return handleResponse<T>(response);
  },

  async patchJson<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: CREDENTIALS,
    });
    return handleResponse<T>(response);
  },

  async putJson<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: CREDENTIALS,
    });
    return handleResponse<T>(response);
  },

  async postForm<T>(path: string, form: FormData): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "POST",
      body: form,
      credentials: CREDENTIALS,
    });
    return handleResponse<T>(response);
  },

  async deleteRequest<T = void>(path: string): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      method: "DELETE",
      credentials: CREDENTIALS,
    });
    return handleResponse<T>(response);
  },

  async postEmpty<T = void>(path: string): Promise<T> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, { method: "POST", credentials: CREDENTIALS });
    return handleResponse<T>(response);
  },
};
