import { useEffect, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { SigmaContainer, useLoadGraph, useRegisterEvents } from "@react-sigma/core";
import { api } from "../../api/client";
import { useStore } from "../../store";

function GraphLoader() {
  const loadGraph = useLoadGraph();
  const registerEvents = useRegisterEvents();
  const { nodes, edges } = useStore();

  useEffect(() => {
    const g = new Graph();
    nodes.forEach((n, i) => {
      const angle = nodes.length > 1 ? (2 * Math.PI * i) / nodes.length : 0;
      g.addNode(n.id, { label: n.label, size: 8, color: "#3b82f6", x: Math.cos(angle), y: Math.sin(angle) });
    });
    edges.forEach((e) => {
      if (g.hasNode(e.source) && g.hasNode(e.target) && !g.hasEdge(e.source, e.target)) {
        g.addEdge(e.source, e.target, { label: e.predicate, color: "#475569" });
      }
    });
    if (g.order > 1) forceAtlas2.assign(g, { iterations: 100 });
    loadGraph(g);
  }, [nodes, edges, loadGraph]);

  useEffect(() => {
    registerEvents({
      clickNode: ({ node }) => console.log("Node clicked:", node),
    });
  }, [registerEvents]);

  return null;
}

export default function GraphView() {
  const { selectedDisease, selectedRegion, setGraph } = useStore();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .graph(selectedDisease ?? undefined, selectedRegion ?? undefined)
      .then((data) => setGraph(data.nodes, data.edges))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedDisease, selectedRegion, setGraph]);

  return (
    <div className="absolute inset-0 flex flex-col">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center z-10 bg-slate-900/60">
          <span className="text-slate-300 text-sm">Chargement du graphe…</span>
        </div>
      )}
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
    </div>
  );
}
