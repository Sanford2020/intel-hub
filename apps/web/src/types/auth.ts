export interface AuthUser {
  id: number;
  email: string;
  role: "admin" | "operator" | "analyst";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: AuthUser;
}

export interface LoginRequest {
  email: string;
  password: string;
}
