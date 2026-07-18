"use client";

import { useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, BrainCircuit, Code, ExternalLink, Lightbulb, CheckCircle2 } from "lucide-react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend. Make sure the API server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  // ── Helpers ──────────────────────────────────────────────────────────
  const getScoreColor = (score: number) => {
    if (score >= 80) return "#22c55e"; // green-500
    if (score >= 60) return "#eab308"; // yellow-500
    if (score >= 40) return "#f97316"; // orange-500
    return "#ef4444"; // red-500
  };

  // ── Sub-components ────────────────────────────────────────────────────
  const ScoreGauge = ({ score, label }: { score: number; label: string }) => {
    const data = [
      { name: "Score", value: score },
      { name: "Empty", value: 100 - score },
    ];
    const color = getScoreColor(score);

    return (
      <div className="flex flex-col items-center justify-center">
        <div className="relative w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={55}
                startAngle={225}
                endAngle={-45}
                dataKey="value"
                stroke="none"
              >
                <Cell fill={color} />
                <Cell fill="#1e293b" /> {/* slate-800 */}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
            <span className="text-2xl font-bold" style={{ color }}>{score}</span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
        </div>
        <span className="text-sm font-medium text-slate-300">{label}</span>
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-600 selection:text-white pb-20">
      
      {/* Navbar / Header */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-blue-500" />
            <h1 className="text-xl font-bold tracking-tight">CiteReady</h1>
          </div>
          <div className="text-sm font-medium px-3 py-1 bg-slate-800 rounded-full text-slate-300 border border-slate-700">
            Enterprise Engine v0.1
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto space-y-8 px-6 pt-12">
        
        {/* Intro */}
        <div className="text-center space-y-3 max-w-2xl mx-auto mb-10">
          <h2 className="text-3xl font-extrabold">Will AI Search Engines Cite You?</h2>
          <p className="text-slate-400">
            Check your Generative Engine Optimization (GEO) score. Our system combines technical SEO metrics with local LLM semantic analysis.
          </p>
        </div>

        {/* Search Bar */}
        <Card className="bg-slate-900 border-slate-800 shadow-md">
          <CardContent className="p-4 sm:p-6">
            <form onSubmit={handleAnalyze} className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <ExternalLink className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="url"
                  required
                  placeholder="https://example.com/blog-post"
                  className="w-full bg-slate-950 border border-slate-700 rounded-md pl-10 pr-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-8 py-3 rounded-md transition-colors whitespace-nowrap"
              >
                {loading ? "Analyzing..." : "Analyze Content"}
              </button>
            </form>
            {error && <p className="text-red-400 mt-4 text-sm font-medium">{error}</p>}
          </CardContent>
        </Card>

        {/* Results Dashboard */}
        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              <Card className="bg-slate-900 border-slate-800 md:col-span-1 flex flex-col justify-center py-6">
                <div className="text-center mb-2">
                  <h3 className="text-lg font-semibold text-slate-200">Blended GEO Score</h3>
                  <p className="text-sm text-slate-500">Final Grade: <span className="font-bold uppercase" style={{color: getScoreColor(result.geo_score)}}>{result.grade}</span></p>
                </div>
                <ScoreGauge score={result.geo_score} label="Overall Score" />
              </Card>

              <Card className="bg-slate-900 border-slate-800 md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5 text-purple-400" />
                    Under The Hood
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col sm:flex-row justify-around items-center gap-6">
                  <ScoreGauge score={result.semantic_score} label="AI Semantic (40%)" />
                  <div className="h-16 w-px bg-slate-800 hidden sm:block"></div>
                  {/* Calculate technical score roughly for display */}
                  <ScoreGauge score={Math.round((result.geo_score - (result.semantic_score * 0.4)) / 0.6) || result.geo_score} label="Technical (60%)" />
                </CardContent>
              </Card>

            </div>

            {/* Insights & Actions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* AI Insights */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    AI Semantic Insights
                  </CardTitle>
                  <p className="text-sm text-slate-500">Direct feedback from the LLM model.</p>
                </CardHeader>
                <CardContent>
                  {result.ai_insights?.length > 0 ? (
                    <ul className="space-y-4">
                      {result.ai_insights.map((insight: string, i: number) => (
                        <li key={i} className="flex gap-3 text-slate-300 text-sm bg-slate-950 p-3 rounded border border-slate-800">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-slate-500 text-sm">No semantic insights available.</p>
                  )}
                </CardContent>
              </Card>

              {/* Priority Actions */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-rose-400" />
                    Priority Fixes
                  </CardTitle>
                  <p className="text-sm text-slate-500">Actionable steps to improve your score.</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4">
                    {result.priority_actions?.map((action: string, i: number) => {
                      const isAi = action.startsWith("🤖");
                      const text = isAi ? action.replace("🤖 AI Insight: ", "") : action;
                      
                      return (
                        <li key={i} className="flex gap-3 text-sm">
                          <div className={`mt-0.5 flex-shrink-0 ${isAi ? 'text-purple-400' : 'text-blue-400'}`}>
                            {isAi ? <BrainCircuit className="w-4 h-4" /> : <Code className="w-4 h-4" />}
                          </div>
                          <span className="text-slate-300">{text}</span>
                        </li>
                      );
                    })}
                  </ul>
                </CardContent>
              </Card>

            </div>
          </div>
        )}

      </div>
    </main>
  );
}
