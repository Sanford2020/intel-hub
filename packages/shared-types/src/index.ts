/** Shared types between frontend and external consumers */

export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface HealthData {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface ChatRequest {
  prompt: string;
  system_prompt?: string;
  prompt_template?: string;
}

export interface ChatResponseData {
  content: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface AgentRole {
  name: string;
  description: string;
  output_format: string;
}
