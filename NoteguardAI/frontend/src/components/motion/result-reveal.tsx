"use client";

import React, { useEffect, useState } from "react";
import { AnimatedCounter } from "@/components/motion/animated-counter";

export interface ResultRevealProps {
  status: "AUTHENTIC" | "COUNTERFEIT" | "UNABLE_TO_DETERMINE" | string;
  confidence: number; // e.g. 98.65
  denominationLabel?: string;
  processingTimeMs?: number;
  children?: React.ReactNode;
}

export const ResultReveal: React.FC<ResultRevealProps> = ({
  status,
  confidence,
  denominationLabel,
  processingTimeMs = 42,
  children
}) => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    setStep(0);
    const t1 = setTimeout(() => setStep(1), 100);
    const t2 = setTimeout(() => setStep(2), 250);
    const t3 = setTimeout(() => setStep(3), 450);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [status, confidence]);

  const isAuthentic = status === "AUTHENTIC" || status === "ACCEPTED";
  const isCounterfeit = status === "COUNTERFEIT";

  return (
    <div className="space-y-6">
      {/* 1. Main Status Banner Reveal */}
      <div
        className={`transition-all duration-400 ease-out transform ${
          step >= 1 ? "opacity-100 translate-y-0 scale-100" : "opacity-0 translate-y-3 scale-98"
        }`}
      >
        <div
          className={`p-6 rounded-xl border flex flex-col sm:flex-row items-center justify-between gap-4 transition-colors ${
            isAuthentic
              ? "bg-emerald-950/20 border-emerald-500/40 text-emerald-400 shadow-[0_0_25px_rgba(16,185,129,0.15)]"
              : isCounterfeit
              ? "bg-red-950/20 border-red-500/40 text-red-400 shadow-[0_0_25px_rgba(239,68,68,0.15)]"
              : "bg-amber-950/20 border-amber-500/40 text-amber-400"
          }`}
        >
          <div className="flex items-center gap-4">
            <div
              className={`h-12 w-12 rounded-xl flex items-center justify-center font-bold text-xl border transition-transform duration-500 ${
                step >= 1 ? "scale-100" : "scale-75"
              } ${
                isAuthentic
                  ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400"
                  : isCounterfeit
                  ? "bg-red-500/10 border-red-500/40 text-red-400 animate-pulse"
                  : "bg-amber-500/10 border-amber-500/40 text-amber-400"
              }`}
            >
              {isAuthentic ? "✓" : isCounterfeit ? "✕" : "!"}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold uppercase tracking-widest text-slate-400">
                  VERIFICATION VERDICT
                </span>
                <span className="text-3xs font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  {processingTimeMs}ms
                </span>
              </div>
              <h2 className="text-2xl font-extrabold font-mono tracking-tight text-slate-100 mt-0.5">
                {isAuthentic
                  ? "AUTHENTIC BANKNOTE"
                  : isCounterfeit
                  ? "COUNTERFEIT DETECTED"
                  : "MANUAL REVIEW REQUIRED"}
              </h2>
            </div>
          </div>

          {denominationLabel && (
            <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
              <span className="text-3xs font-mono uppercase text-slate-500 block">DENOMINATION</span>
              <span className="text-xl font-bold font-mono text-slate-100">{denominationLabel}</span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Confidence Score Gauge Reveal */}
      <div
        className={`transition-all duration-500 ease-out transform ${
          step >= 2 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
        }`}
      >
        <div className="panel-raised p-6 flex flex-col md:flex-row items-center justify-between gap-6 border border-slate-800">
          <div className="flex items-center gap-4">
            <div className="text-left">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                MODEL CONFIDENCE SCORE
              </span>
              <div className="text-3xl font-extrabold font-mono text-emerald-400 tracking-tight mt-1">
                <AnimatedCounter value={confidence} decimals={1} suffix="%" />
              </div>
            </div>
          </div>

          {/* Confidence Bar Track */}
          <div className="flex-1 max-w-md w-full">
            <div className="flex items-center justify-between text-2xs font-mono text-slate-400 mb-1.5">
              <span>0% THRESHOLD</span>
              <span>POLICY PASS &ge; 80%</span>
            </div>
            <div className="w-full h-3 panel-recessed overflow-hidden p-0.5">
              <div
                className={`h-full rounded transition-all duration-1000 ease-out ${
                  isAuthentic
                    ? "bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_12px_#10B981]"
                    : "bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_12px_#EF4444]"
                }`}
                style={{ width: step >= 2 ? `${Math.min(confidence, 100)}%` : "0%" }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* 3. Detailed Breakdown Content Reveal */}
      <div
        className={`transition-all duration-500 ease-out transform ${
          step >= 3 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
        }`}
      >
        {children}
      </div>
    </div>
  );
};
