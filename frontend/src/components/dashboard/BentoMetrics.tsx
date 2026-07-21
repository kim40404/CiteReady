"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, AreaChart, Area } from "recharts";

interface BentoMetricsProps {
  geoScore: number;
  semanticScore: number;
  technicalScore: number;
  grade: string;
}

// Custom Tooltip for Bar Chart
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 text-zinc-100 p-2 rounded shadow-lg text-sm">
        <p className="font-semibold">{payload[0].payload.name}</p>
        <p className="text-blue-400">Score: {payload[0].value}/100</p>
      </div>
    );
  }
  return null;
};

export function BentoMetrics({ geoScore, semanticScore, technicalScore, grade }: BentoMetricsProps) {
  const gaugeData = [
    { name: "Score", value: geoScore },
    { name: "Empty", value: 100 - geoScore },
  ];

  const barData = [
    { name: "Technical", score: technicalScore },
    { name: "Semantic", score: semanticScore },
  ];

  // Dummy aesthetic trend data for the 3rd card
  const areaData = [
    { value: 20 }, { value: 35 }, { value: 30 }, { value: 50 }, 
    { value: 45 }, { value: 65 }, { value: 60 }, { value: geoScore }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mx-auto">
      
      {/* 1. Main Score Card (Pastel / Muted Color) */}
      <div className="col-span-1 md:col-span-1 bg-[#c2bcff] text-zinc-950 rounded-[24px] p-6 shadow-xl flex flex-col items-center justify-center relative overflow-hidden">
        <div className="text-center z-10 mb-4">
          <h3 className="text-lg font-medium opacity-80 tracking-tight">Blended GEO</h3>
          <p className="text-4xl font-bold tracking-tighter mt-1">{geoScore}<span className="text-xl opacity-60">/100</span></p>
        </div>
        
        <div className="relative w-48 h-24 z-10">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={gaugeData}
                cx="50%"
                cy="100%"
                startAngle={180}
                endAngle={0}
                innerRadius={60}
                outerRadius={80}
                dataKey="value"
                stroke="none"
              >
                <Cell fill="#0a0a0a" /> {/* Deep dark for the fill inside pastel */}
                <Cell fill="rgba(255,255,255,0.4)" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="absolute bottom-6 font-semibold text-zinc-800 bg-white/40 px-4 py-1 rounded-full backdrop-blur-md">
          Grade {grade}
        </div>
      </div>

      {/* 2. Distribution Card (White Base) */}
      <div className="col-span-1 md:col-span-1 bg-white text-zinc-900 rounded-[24px] p-6 shadow-xl flex flex-col">
        <h3 className="text-lg font-medium tracking-tight mb-6">Score Distribution</h3>
        <div className="flex-1 w-full min-h-[120px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#71717a', fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa', fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f4f4f5' }} />
              <Bar dataKey="score" fill="#18181b" radius={[6, 6, 6, 6]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Trend/Aesthetic Card */}
      <div className="col-span-1 md:col-span-1 bg-zinc-900 text-zinc-100 rounded-[24px] p-6 shadow-xl border border-zinc-800/80 flex flex-col relative overflow-hidden">
        <h3 className="text-lg font-medium tracking-tight z-10 text-zinc-300">Visibility Trend</h3>
        <p className="text-3xl font-semibold mt-2 z-10">+{Math.round(geoScore * 0.15)}%</p>
        <p className="text-xs text-zinc-500 z-10 mt-1">Simulated impact over 30 days</p>
        
        <div className="absolute bottom-0 left-0 right-0 h-2/3 opacity-70 pointer-events-none">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={areaData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#c2bcff" stopOpacity={0.5}/>
                  <stop offset="95%" stopColor="#c2bcff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="value" stroke="#c2bcff" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
