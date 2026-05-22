import { create } from "zustand";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

interface GraphNode {
  id: string;
  label: string;
}

interface GraphEdge {
  source: string;
  target: string;
  predicate: string;
}

interface AppState {
  // Filtres globaux
  selectedDisease: string | null;
  selectedRegion: string | null;
  setFilter: (disease: string | null, region: string | null) => void;

  // Chat NLP
  messages: Message[];
  isQuerying: boolean;
  addMessage: (msg: Message) => void;
  setQuerying: (v: boolean) => void;

  // Graphe
  nodes: GraphNode[];
  edges: GraphEdge[];
  setGraph: (nodes: GraphNode[], edges: GraphEdge[]) => void;

  // API status
  backendOnline: boolean;
  setBackendOnline: (v: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  selectedDisease: null,
  selectedRegion: null,
  setFilter: (disease, region) => set({ selectedDisease: disease, selectedRegion: region }),

  messages: [],
  isQuerying: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setQuerying: (v) => set({ isQuerying: v }),

  nodes: [],
  edges: [],
  setGraph: (nodes, edges) => set({ nodes, edges }),

  backendOnline: false,
  setBackendOnline: (v) => set({ backendOnline: v }),
}));
