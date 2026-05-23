const TOKEN_KEY = "ih_access_token";
const AUTH_COOKIE = "ih_auth";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
  document.cookie = `${AUTH_COOKIE}=1; path=/; SameSite=Lax`;
}

export function clearAccessToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
  document.cookie = `${AUTH_COOKIE}=; path=/; Max-Age=0`;
}
