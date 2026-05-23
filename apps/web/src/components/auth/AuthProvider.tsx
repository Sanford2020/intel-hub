"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiClient } from "@/lib/api";
import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/auth-storage";
import type { AuthUser, LoginResponse } from "@/types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (payload: { email: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    apiClient
      .get<AuthUser>("/api/v1/auth/me")
      .then((profile) => setUser(profile))
      .catch(() => {
        clearAccessToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (credentials: { email: string; password: string }) => {
    const response = await apiClient.post<LoginResponse>("/api/v1/auth/login", credentials);
    setAccessToken(response.access_token);
    setUser(response.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.post("/api/v1/auth/logout");
    } catch {
      // Ignore network errors during logout.
    }
    clearAccessToken();
    setUser(null);
    window.location.href = "/login";
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
