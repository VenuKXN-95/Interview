import api from "./api";
import { SubmitAnswerRequest, SubmitAnswerResponse, AnswerListResponse } from "@/types";

export const answerService = {
  submit: async (body: SubmitAnswerRequest): Promise<SubmitAnswerResponse> => {
    const { data } = await api.post<SubmitAnswerResponse>("/answer/submit", body);
    return data;
  },

  getSessionAnswers: async (sessionId: string): Promise<AnswerListResponse> => {
    const { data } = await api.get<AnswerListResponse>(`/answer/session/${sessionId}`);
    return data;
  },
};
