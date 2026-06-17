import api from "./api";
import { ResumeUploadResponse, ResumeGetResponse } from "@/types";

export const resumeService = {
  upload: async (file: File): Promise<ResumeUploadResponse> => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post<ResumeUploadResponse>("/resume/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  get: async (resumeId: string): Promise<ResumeGetResponse> => {
    const { data } = await api.get<ResumeGetResponse>(`/resume/${resumeId}`);
    return data;
  },
};
