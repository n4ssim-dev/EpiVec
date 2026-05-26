import axios from "axios";

const http = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10_000,
});

const httpSlow = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 120_000,
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

export interface StatsData {
  graph: { nodes: number; edges: number };
  centrality: { top_diseases: { node: string; score: number }[] };
}

export const api = {
  health: () => http.get<{ status: string }>("/health").then((r) => r.data),

  query: (question: string) =>
    httpSlow.post<QueryResponse>("/query/", { question }).then((r) => r.data),

  graph: (disease?: string, region?: string, depth = 2) =>
    http.get<GraphData>("/graph/", { params: { disease, region, depth } }).then((r) => r.data),

  stats: () =>
    http.get<StatsData>("/graph/stats").then((r) => r.data),

  ingest: (source: string) =>
    httpSlow.post(`/ingest/${source}`).then((r) => r.data),
};
