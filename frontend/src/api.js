import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export const extractFromText = (text) =>
  api.post("/api/extract/text", { text }).then((r) => r.data);

export const extractFromFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/api/extract/file", formData).then((r) => r.data);
};

export const chatWithAssistant = (message, currentFormState) =>
  api
    .post("/api/chat", { message, current_form_state: currentFormState })
    .then((r) => r.data);

export const saveComplaint = (formData) =>
  api.post("/api/complaints", formData).then((r) => r.data);

export default api;

