import api from "./api";
import {
  GenerateInterviewRequest,
  GenerateInterviewResponse,
  SessionResponse,
} from "@/types";

export const interviewService = {
  generate: async (body: GenerateInterviewRequest): Promise<GenerateInterviewResponse> => {
    const { data } = await api.post<GenerateInterviewResponse>("/interview/generate", body);
    return data;
  },

  getSession: async (sessionId: string): Promise<SessionResponse> => {
    const { data } = await api.get<SessionResponse>(`/session/${sessionId}`);
    return data;
  },

  startSession: async (sessionId: string): Promise<SessionResponse> => {
    const { data } = await api.post<SessionResponse>(`/session/${sessionId}/start`);
    return data;
  },

  endSession: async (sessionId: string): Promise<SessionResponse> => {
    const { data } = await api.post<SessionResponse>(`/session/${sessionId}/end`);
    return data;
  },
};
