import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { api, StatsData } from "../../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .stats()
      .then(setStats)
      .catch(() => setError("Impossible de récupérer les métriques. Le backend est-il démarré ?"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-slate-400 text-sm animate-pulse">Chargement des métriques…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const { graph, centrality } = stats;
  const barData = centrality.top_diseases.map((d) => ({
    name: d.node.replace("disease:", ""),
    pagerank: d.score,
  }));

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <h2 className="text-lg font-semibold text-slate-100">Métriques du graphe de connaissances</h2>

      {/* Compteurs */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Nœuds</p>
          <p className="text-3xl font-bold text-blue-400">{graph.nodes.toLocaleString()}</p>
          <p className="text-xs text-slate-500 mt-1">entités dans le graphe</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Relations</p>
          <p className="text-3xl font-bold text-emerald-400">{graph.edges.toLocaleString()}</p>
          <p className="text-xs text-slate-500 mt-1">triples de connaissance</p>
        </div>
      </div>

      {/* Graphe PageRank */}
      {barData.length > 0 ? (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-sm font-medium text-slate-300 mb-4">
            Centralité PageRank — maladies les plus connectées
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={barData} layout="vertical" margin={{ left: 16, right: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} width={90} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", fontSize: 12 }}
                formatter={(v: number) => [v.toFixed(4), "PageRank"]}
              />
              <Bar dataKey="pagerank" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 text-center">
          <p className="text-slate-500 text-sm">
            Graphe vide — lancez une ingestion via{" "}
            <code className="text-blue-400">POST /ingest/spf</code>
          </p>
        </div>
      )}

      {/* Explication pédagogique */}
      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50 text-xs text-slate-400 space-y-1">
        <p className="font-medium text-slate-300">Comment lire ce graphe ?</p>
        <p>
          Le <span className="text-blue-300">PageRank</span> mesure l'importance d'un nœud par le
          nombre et la qualité de ses connexions. Une maladie avec un score élevé est reliée à
          de nombreuses régions et métriques dans le graphe de connaissances.
        </p>
      </div>
    </div>
  );
}
