import api from "./api";
import { JDUploadResponse } from "@/types";

export const jdService = {
  upload: async (file: File): Promise<JDUploadResponse> => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post<JDUploadResponse>("/jd/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  submitRaw: async (text: string): Promise<JDUploadResponse> => {
    const { data } = await api.post<JDUploadResponse>("/jd/raw", { text });
    return data;
  },

  get: async (jdId: string): Promise<JDUploadResponse> => {
    const { data } = await api.get<JDUploadResponse>(`/jd/${jdId}`);
    return data;
  },
};
