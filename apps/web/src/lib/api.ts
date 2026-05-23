import { clearAccessToken, getAccessToken } from "@/lib/auth-storage";

const REQUEST_TIMEOUT_MS = 15_000;

function resolveApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) return configured;
  if (typeof window !== "undefined") return window.location.origin;
  return "http://127.0.0.1:8000";
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  timeoutMs?: number;
}

class ApiClient {
  private get baseUrl(): string {
    return resolveApiBaseUrl();
  }

  private buildUrl(path: string, params?: Record<string, string>): string {
    const url = new URL(path, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }
    return url.toString();
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { params, timeoutMs = REQUEST_TIMEOUT_MS, signal, ...fetchOptions } = options;
    const url = this.buildUrl(path, params);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    if (signal) {
      signal.addEventListener("abort", () => controller.abort(), { once: true });
    }

    let response: Response;
    try {
      const token = getAccessToken();
      response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...fetchOptions.headers,
        },
      });
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw new ApiError(
          0,
          `API 请求超时（${timeoutMs / 1000}s），请确认后端已启动：${this.baseUrl}`,
        );
      }
      throw new ApiError(
        0,
        `无法连接 API（${this.baseUrl}），请确认 backend 在 8000 端口运行`,
        error,
      );
    } finally {
      clearTimeout(timeoutId);
    }

    if (!response.ok) {
      if (
        response.status === 401 &&
        typeof window !== "undefined" &&
        !path.includes("/auth/login")
      ) {
        clearAccessToken();
        const next = encodeURIComponent(
          `${window.location.pathname}${window.location.search}`,
        );
        window.location.href = `/login?next=${next}`;
      }
      const error = await this.parseBody(response);
      const message =
        this.getErrorMessage(error) || response.statusText || `HTTP ${response.status}`;
      throw new ApiError(response.status, message, error);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return this.parseBody(response) as Promise<T>;
  }

  private async parseBody(response: Response): Promise<unknown> {
    const text = await response.text();
    if (!text) {
      return undefined;
    }

    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      return JSON.parse(text);
    }

    return text;
  }

  private getErrorMessage(error: unknown): string | undefined {
    if (!error) {
      return undefined;
    }

    if (typeof error === "string") {
      return error;
    }

    if (typeof error === "object") {
      const maybeError = error as {
        detail?: unknown;
        error?: { message?: unknown };
        message?: unknown;
      };

      if (typeof maybeError.error?.message === "string") {
        return maybeError.error.message;
      }

      if (typeof maybeError.detail === "string") {
        return maybeError.detail;
      }

      if (typeof maybeError.message === "string") {
        return maybeError.message;
      }
    }

    return undefined;
  }

  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: "GET" });
  }

  async post<T>(path: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(path: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(path: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: "DELETE" });
  }
}

export class ApiError extends Error {
  public status: number;
  public data?: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export const apiClient = new ApiClient();
