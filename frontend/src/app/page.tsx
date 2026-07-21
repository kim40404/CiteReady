"use client";

import { useState } from "react";
import { BrainCircuit } from "lucide-react";
import { PremiumHero } from "@/components/dashboard/PremiumHero";
import { PremiumMetrics } from "@/components/dashboard/PremiumMetrics";
import { PremiumInsights } from "@/components/dashboard/PremiumInsights";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const hasSearched = loading || result || error;

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend. Make sure the API server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-blue-600 selection:text-white pb-32 flex flex-col">
      
      {/* Navbar / Header */}
      <header className="border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-md sticky top-0 z-50 flex-none">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <button 
            onClick={() => { setUrl(""); setResult(null); setError(""); }}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity focus:outline-none cursor-pointer"
          >
            <div className="p-2 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg border border-blue-500/30">
              <BrainCircuit className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-zinc-100 to-zinc-400">
              CiteReady
            </h1>
          </button>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 rounded-full border border-zinc-800 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-medium text-zinc-300">Engine Online</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col w-full px-6">
        
        {/* Component 1: Premium Hero Input */}
        <PremiumHero 
          value={url}
          onChange={setUrl}
          onSubmit={handleAnalyze}
          loading={loading}
          centered={!hasSearched}
        />

        {error && !loading && (
          <div className="max-w-4xl mx-auto w-full mb-12 animate-in fade-in slide-in-from-top-4">
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-center">
              {error}
            </div>
          </div>
        )}

        {/* Results Dashboard */}
        {result && !loading && (
          <div className="max-w-6xl mx-auto w-full space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700 pb-20">
            
            {/* Component 2: Premium Metrics */}
            <section>
              <PremiumMetrics 
                geoScore={result.geo_score}
                semanticScore={result.semantic_score}
                technicalScore={Math.round((result.geo_score - (result.semantic_score * 0.4)) / 0.6) || result.geo_score}
                grade={result.grade}
              />
            </section>

            {/* Component 3: Premium Insights */}
            <section>
              <PremiumInsights 
                insights={result.ai_insights || []}
                actions={result.priority_actions || []}
              />
            </section>
            
          </div>
        )}

      </div>
    </main>
  );
}
