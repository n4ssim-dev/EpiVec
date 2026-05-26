import { useState } from "react";
import { api } from "../../api/client";

interface Source {
  id: string;
  label: string;
  description: string;
  live: boolean;
}

const SOURCES: Source[] = [
  { id: "spf",        label: "SPF — Hospitalisations COVID",    description: "Santé Publique France · données départementales France",   live: false },
  { id: "ecdc",       label: "ECDC — COVID UE/EEE",             description: "Centre européen de prévention des maladies · cas & décès", live: true  },
  { id: "who",        label: "OMS — COVID mondial",             description: "Organisation Mondiale de la Santé · couverture globale",    live: false },
  { id: "data_gouv",  label: "data.gouv.fr — MDO",              description: "Maladies à déclaration obligatoire · catalogue français",   live: true  },
  { id: "flunet",     label: "FluNet — Grippe saisonnière",      description: "Réseau OMS FluNet · surveillance grippale mondiale",       live: false },
  { id: "mpox",       label: "OMS/ECDC — Mpox",                  description: "Données embarquées · épidémie 2022-2023",                live: false },
  { id: "dengue",     label: "PAHO/OMS — Dengue",               description: "Amériques latines & Asie du Sud-Est · 2023-2024",          live: false },
];

type Status = "idle" | "loading" | "ok" | "error";

export default function DataSources() {
  const [statuses, setStatuses] = useState<Record<string, Status>>(
    Object.fromEntries(SOURCES.map((s) => [s.id, "idle"]))
  );
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [globalLoading, setGlobalLoading] = useState(false);

  const ingest = async (sourceId: string) => {
    setStatuses((prev) => ({ ...prev, [sourceId]: "loading" }));
    try {
      const result = await api.ingest(sourceId);
      setCounts((prev) => ({ ...prev, [sourceId]: result?.records_ingested ?? 0 }));
      setStatuses((prev) => ({ ...prev, [sourceId]: "ok" }));
    } catch {
      setStatuses((prev) => ({ ...prev, [sourceId]: "error" }));
    }
  };

  const ingestAll = async () => {
    setGlobalLoading(true);
    for (const s of SOURCES) {
      await ingest(s.id);
    }
    setGlobalLoading(false);
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Sources de données</h2>
        <button
          onClick={ingestAll}
          disabled={globalLoading}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          {globalLoading ? "Ingestion en cours…" : "Tout ingérer"}
        </button>
      </div>

      <div className="grid gap-3">
        {SOURCES.map((source) => {
          const status = statuses[source.id];
          return (
            <div
              key={source.id}
              className="flex items-center justify-between bg-slate-800 rounded-xl px-4 py-3 border border-slate-700"
            >
              <div className="flex items-start gap-3 min-w-0">
                <StatusDot status={status} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-slate-100 truncate">{source.label}</p>
                    {source.live && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/60 text-emerald-400 border border-emerald-700/50 shrink-0">
                        live
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 truncate">{source.description}</p>
                  {status === "ok" && counts[source.id] !== undefined && (
                    <p className="text-xs text-emerald-400 mt-0.5">
                      {counts[source.id].toLocaleString()} indicateurs indexés
                    </p>
                  )}
                  {status === "error" && (
                    <p className="text-xs text-red-400 mt-0.5">Échec — vérifier que le backend est démarré</p>
                  )}
                </div>
              </div>

              <button
                onClick={() => ingest(source.id)}
                disabled={status === "loading" || globalLoading}
                className="ml-4 shrink-0 px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium transition-colors"
              >
                {status === "loading" ? "…" : "Ingérer"}
              </button>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-slate-500">
        Les sources marquées <span className="text-emerald-400">live</span> tentent une requête
        réseau en temps réel. Les autres utilisent des données embarquées représentatives.
      </p>
    </div>
  );
}

function StatusDot({ status }: { status: Status }) {
  const cls =
    status === "ok"      ? "bg-emerald-400" :
    status === "error"   ? "bg-red-500" :
    status === "loading" ? "bg-yellow-400 animate-pulse" :
                           "bg-slate-600";
  return <span className={`mt-1 w-2 h-2 rounded-full shrink-0 ${cls}`} />;
}
