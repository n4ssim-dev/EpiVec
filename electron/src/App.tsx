import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import Dashboard from "./components/Dashboard";
import GraphView from "./components/GraphView";
import MapView from "./components/MapView";

type Tab = "graph" | "map" | "dashboard" | "chat";

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("graph");

  const tabs: { id: Tab; label: string }[] = [
    { id: "graph", label: "Graphe" },
    { id: "map", label: "Carte" },
    { id: "dashboard", label: "Prédictions" },
    { id: "chat", label: "Analyse NLP" },
  ];

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-slate-800 border-b border-slate-700">
        <h1 className="text-xl font-bold text-blue-400">EpiGraph</h1>
        <nav className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === "graph" && <GraphView />}
        {activeTab === "map" && <MapView />}
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "chat" && <ChatPanel />}
      </main>
    </div>
  );
}
