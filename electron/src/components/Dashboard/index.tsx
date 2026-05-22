import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { api, PredictionData } from "../../api/client";
import { useStore } from "../../store";

export default function Dashboard() {
  const { selectedDisease, selectedRegion } = useStore();
  const [data, setData] = useState<PredictionData | null>(null);
  const [model, setModel] = useState<"sir" | "ml">("sir");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedDisease || !selectedRegion) return;
    setLoading(true);
    api
      .predict(selectedDisease, selectedRegion, model)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedDisease, selectedRegion, model]);

  if (!selectedDisease || !selectedRegion) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <p className="text-sm">Sélectionnez une maladie et une région dans le graphe</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Prédiction — {selectedDisease} / {selectedRegion}
        </h2>
        <div className="flex gap-2">
          {(["sir", "ml"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setModel(m)}
              className={`px-3 py-1 rounded text-xs font-medium ${
                model === m ? "bg-blue-600" : "bg-slate-700 hover:bg-slate-600"
              }`}
            >
              {m.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="text-slate-400 text-sm">Calcul en cours…</p>}

      {data && (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data.predictions}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
            <Legend />
            {model === "sir" ? (
              <>
                <Line type="monotone" dataKey="infected" stroke="#ef4444" dot={false} name="Infectés" />
                <Line type="monotone" dataKey="susceptible" stroke="#3b82f6" dot={false} name="Susceptibles" />
                <Line type="monotone" dataKey="recovered" stroke="#22c55e" dot={false} name="Rétablis" />
              </>
            ) : (
              <Line type="monotone" dataKey="predicted_cases" stroke="#f59e0b" dot={false} name="Cas prédits" />
            )}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
