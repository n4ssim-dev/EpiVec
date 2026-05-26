import { Component, useEffect, useState, type ReactNode } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { SigmaContainer, useLoadGraph, useRegisterEvents } from "@react-sigma/core";
import { api } from "../../api/client";
import { useStore } from "../../store";

// --- Error Boundary -----------------------------------------------------------

class GraphErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; message: string }
> {
  state = { hasError: false, message: "" };

  static getDerivedStateFromError(err: Error) {
    return { hasError: true, message: err.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-8">
          <p className="text-red-400 text-sm font-medium">Le moteur de rendu du graphe a rencontré une erreur.</p>
          <p className="text-slate-500 text-xs">{this.state.message}</p>
          <button
            className="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-slate-200 transition-colors"
            onClick={() => this.setState({ hasError: false, message: "" })}
          >
            Réessayer
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// --- Graph loader (inner Sigma context) ---------------------------------------

function GraphLoader() {
  const loadGraph = useLoadGraph();
  const registerEvents = useRegisterEvents();
  const { nodes, edges } = useStore();

  useEffect(() => {
    const g = new Graph();

    const cleanLabel = (id: string): string => {
      // "disease:COVID-19" → "COVID-19", "region:FR-75@2021-03-15" → "FR-75"
      const withoutPrefix = id.replace(/^(disease:|region:|metric:)/, "");
      return withoutPrefix.split("@")[0];
    };

    nodes.forEach((n, i) => {
      const angle = nodes.length > 1 ? (2 * Math.PI * i) / nodes.length : 0;
      const isDisease = n.id.startsWith("disease:");
      g.addNode(n.id, {
        label: cleanLabel(n.id),
        size: isDisease ? 16 : 6,
        color: isDisease ? "#f59e0b" : "#3b82f6",
        x: Math.cos(angle),
        y: Math.sin(angle),
      });
    });

    edges.forEach((e) => {
      if (g.hasNode(e.source) && g.hasNode(e.target) && !g.hasEdge(e.source, e.target)) {
        g.addEdge(e.source, e.target, { label: e.predicate, color: "#475569" });
      }
    });

    if (g.order > 1 && g.order <= 300) {
      forceAtlas2.assign(g, { iterations: 150, settings: { gravity: 1 } });
    }

    loadGraph(g);
  }, [nodes, edges, loadGraph]);

  useEffect(() => {
    registerEvents({
      clickNode: ({ node }) => console.log("Node clicked:", node),
    });
  }, [registerEvents]);

  return null;
}

// --- Main component -----------------------------------------------------------

export default function GraphView() {
  const { selectedDisease, selectedRegion, setGraph } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .graph(selectedDisease ?? undefined, selectedRegion ?? undefined)
      .then((data) => setGraph(data.nodes ?? [], data.edges ?? []))
      .catch((err) => setError(err?.message ?? "Erreur de chargement du graphe"))
      .finally(() => setLoading(false));
  }, [selectedDisease, selectedRegion, setGraph]);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 flex flex-col">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center z-10 bg-slate-900/60">
          <span className="text-slate-300 text-sm animate-pulse">Chargement du graphe…</span>
        </div>
      )}
      <GraphErrorBoundary>
        <SigmaContainer
          style={{ flex: 1, minHeight: 0, width: "100%", position: "relative", background: "#0f172a" }}
          settings={{
            renderEdgeLabels: false,
            defaultEdgeColor: "#334155",
            labelColor: { color: "#94a3b8" },
            allowInvalidContainer: true,
          }}
        >
          <GraphLoader />
        </SigmaContainer>
      </GraphErrorBoundary>
    </div>
  );
}
