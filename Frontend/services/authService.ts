import api from "./api";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/auth";

export const authService = {
  register: async (req: RegisterRequest): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/register", req);
    return data;
  },

  login: async (req: LoginRequest): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/login", req);
    return data;
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },

  logout: () => {
    // Token cleanup is handled by the store; nothing server-side in V1
  },
};
