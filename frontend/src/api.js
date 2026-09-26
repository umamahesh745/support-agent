import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 120000, // agent ki 2 min varaku wait
});

export const sendMessage = (message, conversationId) =>
  api.post("/chat", { message, conversation_id: conversationId }).then((r) => r.data);

export const getStats = () => api.get("/stats").then((r) => r.data);

export const getTickets = () => api.get("/tickets").then((r) => r.data);

export const getMessages = (conversationId) =>
  api.get(`/conversations/${conversationId}/messages`).then((r) => r.data);