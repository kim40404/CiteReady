"use client";

import { Search, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface PremiumHeroProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  centered: boolean;
}

export function PremiumHero({ value, onChange, onSubmit, loading, centered }: PremiumHeroProps) {
  return (
    <motion.section 
      layout
      className={`w-full max-w-4xl mx-auto flex flex-col items-center justify-center ${
        centered ? "min-h-[calc(100vh-160px)]" : "pt-12 pb-8"
      }`}
    >
      <div className="text-center space-y-6 mb-12 w-full">
        <motion.h2 
          layout
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }} // smooth, non-bouncy easing
          className="text-white text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-tight"
        >
          Analyze Your Enterprise <br className="hidden sm:block" /> Search Visibility
        </motion.h2>
        
        <motion.p 
          layout
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-zinc-400 text-lg sm:text-xl max-w-2xl mx-auto font-medium"
        >
          Evaluate your Generative Engine Optimization (GEO) score. See exactly what AI search engines 
          like ChatGPT and Perplexity think of your content.
        </motion.p>
      </div>

      <motion.div 
        layout 
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-3xl mx-auto px-4 sm:px-0"
      >
        <form onSubmit={onSubmit} className="flex flex-col sm:flex-row gap-4 w-full relative">
          <div className="relative flex-1 group">
            <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-zinc-500 group-focus-within:text-zinc-300 transition-colors" />
            </div>
            <input
              type="url"
              required
              value={value}
              onChange={(e) => onChange(e.target.value)}
              disabled={loading}
              placeholder="https://your-domain.com/article"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-2xl py-5 pl-14 pr-4 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-xl shadow-sm disabled:opacity-60"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !value}
            className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-medium text-xl px-10 py-5 rounded-2xl transition-all shadow-sm disabled:opacity-60 disabled:hover:bg-blue-600 whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-blue-500/50 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 mr-3 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Content"
            )}
          </button>
        </form>
        
        {/* Helper Text */}
        <div className="mt-6 text-center sm:text-left flex flex-col sm:flex-row justify-between items-center text-sm sm:text-base text-zinc-500 font-medium">
          <p>Example: https://www.google.com/</p>
          <p className="mt-2 sm:mt-0">Supports public pages and blog posts</p>
        </div>
      </motion.div>
    </motion.section>
  );
}
