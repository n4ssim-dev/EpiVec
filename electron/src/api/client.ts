import axios from "axios";

const http = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 30_000,
});

export interface QueryResponse {
  answer: string;
  sources: string[];
  entities: Record<string, string[]>;
  intent: string;
}

export interface GraphData {
  nodes: { id: string; label: string }[];
  edges: { source: string; target: string; predicate: string }[];
  count: { nodes: number; edges: number };
}

export interface PredictionData {
  disease: string;
  region: string;
  model: string;
  horizon_days: number;
  predictions: Record<string, number>[];
}

export const api = {
  health: () => http.get<{ status: string }>("/health").then((r) => r.data),

  query: (question: string) =>
    http.post<QueryResponse>("/query/", { question }).then((r) => r.data),

  graph: (disease?: string, region?: string, depth = 2) =>
    http.get<GraphData>("/graph/", { params: { disease, region, depth } }).then((r) => r.data),

  predict: (disease: string, region: string, model: "sir" | "ml" = "sir", days = 30) =>
    http
      .get<PredictionData>(`/predict/${disease}`, { params: { region, model, days } })
      .then((r) => r.data),

  ingest: (source: string) =>
    http.post(`/ingest/${source}`).then((r) => r.data),
};
