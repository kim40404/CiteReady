"use client";

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

interface VanishInputProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
}

const placeholders = [
  "Enter your enterprise staging URL...",
  "Paste a production blog post link...",
  "Analyze your competitor's GEO score...",
  "Check documentation semantic visibility...",
];

export function VanishInput({ value, onChange, onSubmit, loading }: VanishInputProps) {
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form
        onSubmit={onSubmit}
        className="relative flex items-center w-full bg-zinc-900/80 border border-zinc-800/80 rounded-full px-6 py-4 shadow-xl focus-within:ring-1 focus-within:ring-zinc-700 focus-within:border-zinc-700 transition-all duration-300"
      >
        <div className="relative flex-1 h-8 flex items-center overflow-hidden">
          {/* Animated Placeholders */}
          <AnimatePresence mode="wait">
            {!value && (
              <motion.span
                key={currentPlaceholder}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -20, opacity: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="absolute text-zinc-500 pointer-events-none select-none text-lg truncate"
              >
                {placeholders[currentPlaceholder]}
              </motion.span>
            )}
          </AnimatePresence>
          
          <input
            type="url"
            required
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={loading}
            className="w-full h-full bg-transparent text-zinc-100 text-lg outline-none placeholder:text-transparent disabled:opacity-50"
            aria-label="Target URL"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !value}
          className="ml-4 flex items-center justify-center w-10 h-10 rounded-full bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-zinc-400 border-t-zinc-100 rounded-full animate-spin" />
          ) : (
            <ArrowRight className="w-5 h-5 text-zinc-300" />
          )}
        </button>
      </form>
    </div>
  );
}
