import { FormEvent, useRef, useState } from "react";
import { api } from "../../api/client";
import { useStore } from "../../store";

export default function ChatPanel() {
  const { messages, isQuerying, addMessage, setQuerying } = useStore();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || isQuerying) return;

    setInput("");
    addMessage({ role: "user", content: question });
    setQuerying(true);

    try {
      const resp = await api.query(question);
      addMessage({ role: "assistant", content: resp.answer, sources: resp.sources });
    } catch {
      addMessage({ role: "assistant", content: "Erreur : impossible de contacter le backend." });
    } finally {
      setQuerying(false);
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-slate-500 text-center mt-16">
            Posez une question épidémiologique en français…
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-2xl px-4 py-3 rounded-xl text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-700 text-slate-100"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <p className="mt-2 text-xs text-slate-400">
                  Sources : {msg.sources.join(", ")}
                </p>
              )}
            </div>
          </div>
        ))}
        {isQuerying && (
          <div className="flex justify-start">
            <div className="bg-slate-700 px-4 py-3 rounded-xl text-slate-400 text-sm animate-pulse">
              Analyse en cours…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ex : Combien de cas de grippe en Île-de-France en janvier 2024 ?"
          className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
          disabled={isQuerying}
        />
        <button
          type="submit"
          disabled={isQuerying || !input.trim()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-lg text-sm font-medium transition-colors"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
