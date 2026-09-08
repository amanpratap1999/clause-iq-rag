"use client";

import React, { useState } from 'react';

interface Citation {
  document_name: string;
  page_number: number;
  clause: string;
  snippet: string;
  score: number;
}

interface QueryResponse {
  question: string;
  answer: string;
  citations: Citation[];
  latency_ms: number;
  mode: string;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string; citations?: Citation[]; latency?: number }>>([
    {
      role: 'assistant',
      text: 'Hello! I am your Policy & Contract Assistant. Ask me anything about employee policies, vendor SLAs, security standards, or terms of service to get exact page-level citations.'
    }
  ]);

  const handleSend = async (questionText?: string) => {
    const q = questionText || query;
    if (!q.trim() || loading) return;

    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8001/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, top_k: 3 })
      });
      const data: QueryResponse = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.answer,
          citations: data.citations,
          latency: data.latency_ms
        }
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Error contacting backend API. Please make sure the FastAPI server is running.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col text-slate-900">
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📜</span>
            <div>
              <h1 className="font-bold text-lg">Policy & Contract Q&A (Next.js)</h1>
              <p className="text-xs text-slate-500">Autonomous RAG with Page Citations</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto flex-1 w-full p-4 flex flex-col gap-4">
        {/* Chat window */}
        <div className="flex-1 bg-white rounded-xl border border-slate-200 p-6 overflow-y-auto space-y-6 min-h-[400px]">
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`p-4 rounded-2xl max-w-2xl ${m.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-50 border border-slate-200 rounded-tl-none'}`}>
                <p className="text-sm leading-relaxed">{m.text}</p>
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-200">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Verified Citations:</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {m.citations.map((c, ci) => (
                        <div key={ci} className="bg-white p-3 rounded-lg border border-indigo-200 text-xs shadow-xs">
                          <div className="flex justify-between items-center font-medium text-slate-800">
                            <span>📄 {c.document_name}</span>
                            <span className="bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded text-[11px] font-mono">Page {c.page_number}</span>
                          </div>
                          <p className="text-[11px] text-indigo-600 mt-1 font-medium">{c.clause}</p>
                          <p className="text-[11px] text-slate-500 italic mt-1 border-l-2 border-indigo-300 pl-2">"{c.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {m.latency && (
                  <p className="text-[10px] text-slate-400 mt-2">⚡ Response time: {m.latency} ms</p>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-xs text-slate-500 animate-pulse">Searching policies and verifying citations...</div>
          )}
        </div>

        {/* Input */}
        <div className="bg-white p-2 rounded-xl border border-slate-200 flex gap-2 shadow-sm">
          <input
            type="text"
            className="flex-1 px-4 py-2 text-sm outline-none"
            placeholder="Ask a question about travel expenses, SLAs, equipment stipend..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button
            onClick={() => handleSend()}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition"
          >
            Ask
          </button>
        </div>
      </div>
    </main>
  );
}
