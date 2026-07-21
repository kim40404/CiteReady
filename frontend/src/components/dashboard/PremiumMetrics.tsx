"use client";

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

interface PremiumMetricsProps {
  geoScore: number;
  semanticScore: number;
  technicalScore: number;
  grade: string;
}

export function PremiumMetrics({ geoScore, semanticScore, technicalScore, grade }: PremiumMetricsProps) {
  // Main Gauge Data
  const gaugeData = [
    { name: "Score", value: geoScore },
    { name: "Empty", value: 100 - geoScore },
  ];

  // Grade Colors for consistency
  const getGradeColor = (g: string) => {
    switch(g.toUpperCase()) {
      case 'A': return 'text-emerald-400';
      case 'B': return 'text-blue-400';
      case 'C': return 'text-yellow-400';
      case 'D': return 'text-orange-400';
      default: return 'text-red-400';
    }
  };

  const getGaugeColor = (g: string) => {
    switch(g.toUpperCase()) {
      case 'A': return '#34d399'; // emerald-400
      case 'B': return '#60a5fa'; // blue-400
      case 'C': return '#facc15'; // yellow-400
      case 'D': return '#fb923c'; // orange-400
      default: return '#f87171'; // red-400
    }
  };

  const gradeColorClass = getGradeColor(grade);
  const gaugeColor = getGaugeColor(grade);

  return (
    <div className="w-full max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      
      {/* Primary Score Card */}
      <div className="col-span-1 md:col-span-1 bg-zinc-900 border border-zinc-800 rounded-2xl p-8 flex flex-col items-center justify-center relative shadow-sm">
        <h3 className="text-zinc-400 text-sm font-medium tracking-wide uppercase mb-6">Blended GEO Score</h3>
        
        <div className="relative w-48 h-24">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={gaugeData}
                cx="50%"
                cy="100%"
                startAngle={180}
                endAngle={0}
                innerRadius={70}
                outerRadius={90}
                dataKey="value"
                stroke="none"
              >
                <Cell fill={gaugeColor} />
                <Cell fill="#27272a" /> {/* zinc-800 */}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute bottom-0 left-0 right-0 flex flex-col items-center justify-center translate-y-4">
            <span className="text-5xl font-bold tracking-tighter text-zinc-100">{geoScore}</span>
          </div>
        </div>
        
        <div className="mt-8 flex items-center gap-2">
          <span className="text-zinc-400 text-sm">Final Grade:</span>
          <span className={`text-xl font-bold ${gradeColorClass}`}>{grade}</span>
        </div>
      </div>

      {/* Sub-metrics Card */}
      <div className="col-span-1 md:col-span-2 bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-sm flex flex-col justify-center space-y-10">
        
        {/* Technical Score */}
        <div className="space-y-3">
          <div className="flex justify-between items-end">
            <div>
              <h3 className="text-zinc-100 font-medium text-lg">Technical Structure</h3>
              <p className="text-zinc-500 text-sm">HTML metadata, schemas, and crawlability.</p>
            </div>
            <span className="text-2xl font-semibold text-zinc-300">{technicalScore}<span className="text-zinc-600 text-lg">/100</span></span>
          </div>
          <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 rounded-full transition-all duration-1000 ease-out" 
              style={{ width: `${technicalScore}%` }}
            />
          </div>
        </div>

        {/* Semantic Score */}
        <div className="space-y-3">
          <div className="flex justify-between items-end">
            <div>
              <h3 className="text-zinc-100 font-medium text-lg">AI Semantic Authority</h3>
              <p className="text-zinc-500 text-sm">Fact density, credibility, and language clarity.</p>
            </div>
            <span className="text-2xl font-semibold text-zinc-300">{semanticScore}<span className="text-zinc-600 text-lg">/100</span></span>
          </div>
          <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-purple-500 rounded-full transition-all duration-1000 ease-out" 
              style={{ width: `${semanticScore}%` }}
            />
          </div>
        </div>

      </div>

    </div>
  );
}
