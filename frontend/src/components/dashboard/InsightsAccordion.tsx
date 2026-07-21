"use client";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { BrainCircuit, Code, AlertTriangle, ShieldCheck } from "lucide-react";

interface InsightsAccordionProps {
  insights: string[];
  actions: string[];
}

export function InsightsAccordion({ insights, actions }: InsightsAccordionProps) {
  // Combine insights and actions for the accordion
  const items = [
    ...insights.map((insight, idx) => ({
      id: `insight-${idx}`,
      type: "semantic",
      title: insight,
      detail: "This insight is provided by the AI semantic engine based on language quality, authority, and fact density.",
      icon: <BrainCircuit className="w-5 h-5 text-purple-400" />
    })),
    ...actions.map((action, idx) => {
      const isAi = action.startsWith("🤖");
      const text = isAi ? action.replace("🤖 AI Insight: ", "") : action;
      return {
        id: `action-${idx}`,
        type: "technical",
        title: text,
        detail: isAi 
          ? "Action recommended by the semantic engine."
          : "Action recommended by the technical SEO parser. Fix this in your HTML structure.",
        icon: isAi ? <BrainCircuit className="w-5 h-5 text-purple-400" /> : <Code className="w-5 h-5 text-blue-400" />
      };
    })
  ];

  const totalIssues = actions.length;
  const severityColor = totalIssues > 5 ? "text-red-400" : totalIssues > 2 ? "text-yellow-400" : "text-green-400";
  const SeverityIcon = totalIssues > 2 ? AlertTriangle : ShieldCheck;

  return (
    <div className="w-full max-w-5xl mx-auto bg-zinc-900 border border-zinc-800/80 rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row">
      
      {/* Left Column: Media / Severity Area */}
      <div className="md:w-1/3 bg-zinc-950 p-8 flex flex-col justify-center items-start border-r border-zinc-800/80">
        <div className={`p-4 rounded-2xl bg-zinc-900 border border-zinc-800 mb-6 ${severityColor}`}>
          <SeverityIcon className="w-10 h-10" />
        </div>
        <h3 className="text-2xl font-semibold text-zinc-100 tracking-tight mb-2">Audit Findings</h3>
        <p className="text-zinc-400 text-sm leading-relaxed mb-8">
          Review the specific AI semantic insights and technical SEO bottlenecks found in your content structure.
        </p>
        
        {/* Simple severity bar representation */}
        <div className="w-full space-y-3">
          <div className="w-full">
            <div className="flex justify-between text-xs text-zinc-500 mb-1">
              <span>Technical Debt</span>
              <span>{actions.filter(a => !a.startsWith("🤖")).length} items</span>
            </div>
            <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(100, actions.length * 15)}%` }}></div>
            </div>
          </div>
          <div className="w-full">
            <div className="flex justify-between text-xs text-zinc-500 mb-1">
              <span>Semantic Gaps</span>
              <span>{insights.length} items</span>
            </div>
            <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${Math.min(100, insights.length * 20)}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Accordion List */}
      <div className="md:w-2/3 p-6 sm:p-8 max-h-[600px] overflow-y-auto custom-scrollbar">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-500 space-y-4">
            <ShieldCheck className="w-12 h-12 opacity-50" />
            <p>No issues found. Your content is perfectly optimized.</p>
          </div>
        ) : (
          <Accordion type="single" collapsible={true} className="w-full space-y-4">
            {items.map((item) => (
              <AccordionItem 
                key={item.id} 
                value={item.id}
                className="border border-transparent bg-transparent rounded-xl px-4 data-[state=open]:bg-zinc-800 data-[state=open]:border-zinc-700 data-[state=open]:shadow-xl data-[state=open]:translate-x-1 transition-all duration-300"
              >
                <AccordionTrigger className="hover:no-underline py-4 text-left">
                  <div className="flex items-start gap-4 pr-4">
                    <div className="mt-0.5 flex-shrink-0">{item.icon}</div>
                    <span className="text-sm sm:text-base font-medium text-zinc-200 leading-snug">{item.title}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="text-zinc-400 text-sm pb-5 pl-9">
                  {item.detail}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </div>
    </div>
  );
}
