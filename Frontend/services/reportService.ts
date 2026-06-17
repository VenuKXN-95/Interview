import api from "./api";
import { ReportResponse } from "@/types";
import { API_BASE_URL } from "@/lib/constants";

export const reportService = {
  getJson: async (sessionId: string): Promise<ReportResponse> => {
    const { data } = await api.get<ReportResponse>(`/report/${sessionId}/json`);
    return data;
  },

  getPdfUrl: (sessionId: string): string => {
    return `${API_BASE_URL}/report/${sessionId}`;
  },

  downloadPdf: async (sessionId: string): Promise<Blob> => {
    const { data } = await api.get(`/report/${sessionId}`, {
      responseType: "blob",
    });
    return data;
  },
};
