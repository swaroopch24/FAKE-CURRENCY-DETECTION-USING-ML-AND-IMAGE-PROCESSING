"use client";

import React from "react";

export interface ConfidenceGaugeProps {
  score?: number;
  verdict?: "GENUINE" | "COUNTERFEIT" | "SUSPICIOUS" | "PENDING";
  modelName?: string;
}

export const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({
  score = 0,
  verdict = "PENDING",
  modelName = "MobileNetV2 (v1.0)"
}) => {
  // SVG Arc calculation
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="panel-raised p-6 flex flex-col justify-between select-none border border-slate-700/60 h-full">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="led-emerald" />
          <span className="text-2xs font-mono font-bold tracking-wider text-slate-300 uppercase">
            CLASSIFICATION PREVIEW
          </span>
        </div>
        <span className="text-3xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
          DEMO ONLY
        </span>
      </div>

      {/* Main Gauge Visual */}
      <div className="flex flex-col items-center justify-center my-auto py-2">
        <div className="relative w-36 h-36 flex items-center justify-center">
          {/* Circular SVG Gauge Meter */}
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            {/* Background Track */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-slate-850 stroke-current"
              strokeWidth="10"
              fill="transparent"
            />
            {/* Active Emerald Progress Ring */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-emerald-400 stroke-current transition-all duration-1000 ease-out"
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              style={{
                filter: "drop-shadow(0px 0px 8px rgba(16, 185, 129, 0.6))"
              }}
            />
          </svg>

          {/* Centered Readout Value */}
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-extrabold font-mono text-slate-100 tracking-tight">
              {score}%
            </span>
            <span className="text-[10px] font-mono font-semibold tracking-wider text-emerald-400 uppercase">
              {verdict}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Readouts & Model Metadata */}
      <div className="panel-recessed p-3 mt-4 space-y-2 text-2xs font-mono">
        <div className="flex items-center justify-between text-slate-400">
          <span>CONFIDENCE LEVEL</span>
          <span className="text-emerald-400 font-bold">80% BOTH SCORES</span>
        </div>
        <div className="flex items-center justify-between text-slate-400 border-t border-slate-850 pt-1.5">
          <span>VISION ENGINE</span>
          <span className="text-slate-200 font-semibold">{modelName}</span>
        </div>
        <div className="flex items-center justify-between text-slate-400 border-t border-slate-850 pt-1.5">
          <span>IMAGE RESIZE</span>
          <span className="text-blue-400 font-semibold">BILINEAR</span>
        </div>
      </div>
    </div>
  );
};
