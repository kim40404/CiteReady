"use client";

import { BrainCircuit, Code, CheckCircle2, AlertCircle } from "lucide-react";

interface PremiumInsightsProps {
  insights: string[];
  actions: string[];
}

export function PremiumInsights({ insights, actions }: PremiumInsightsProps) {
  return (
    <div className="w-full max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      
      {/* AI Reasoning Card */}
      <div className="col-span-1 bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-sm flex flex-col">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-purple-500/10 rounded-lg">
            <BrainCircuit className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-zinc-100 tracking-tight">AI Reasoning</h3>
            <p className="text-sm text-zinc-500">Direct evaluation from the semantic engine</p>
          </div>
        </div>
        
        <div className="flex-1 space-y-4">
          {insights.length === 0 ? (
            <p className="text-zinc-500 italic">No semantic insights generated.</p>
          ) : (
            insights.map((insight, idx) => (
              <div key={idx} className="flex gap-4 items-start bg-zinc-950/50 p-4 rounded-xl border border-zinc-800/50">
                <CheckCircle2 className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
                <p className="text-zinc-300 leading-relaxed text-sm sm:text-base">{insight}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Priority Fixes Card */}
      <div className="col-span-1 bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-sm flex flex-col">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Code className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-zinc-100 tracking-tight">Priority Fixes</h3>
            <p className="text-sm text-zinc-500">Actionable steps to improve crawler visibility</p>
          </div>
        </div>
        
        <div className="flex-1 space-y-4">
          {actions.filter(a => !a.startsWith("🤖")).length === 0 ? (
            <p className="text-zinc-500 italic">No technical issues found. Excellent structure!</p>
          ) : (
            actions.filter(a => !a.startsWith("🤖")).map((action, idx) => (
              <div key={idx} className="flex gap-4 items-start bg-zinc-950/50 p-4 rounded-xl border border-zinc-800/50">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-blue-400" />
                <p className="text-zinc-300 leading-relaxed text-sm sm:text-base">{action}</p>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
