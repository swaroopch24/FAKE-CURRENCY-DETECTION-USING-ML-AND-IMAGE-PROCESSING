"use client";

import React, { useState } from "react";

export const BanknoteScanner = () => {
  const [activeTab, setActiveTab] = useState<"visual" | "uv" | "microtext">("visual");

  return (
    <div className="panel-raised p-6 relative overflow-hidden select-none border border-slate-700/60">
      {/* Top Header / Instrument Status Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-5">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-md border border-slate-800">
            <span className="led-emerald led-emerald-pulse" />
            <span className="text-2xs font-mono tracking-wider text-emerald-400 uppercase font-semibold">
              SCANNER PREVIEW
            </span>
          </div>
          <span className="text-2xs font-mono text-slate-500 hidden sm:inline-block">
            Illustrative image only — no live scan or optical sensor.
          </span>
        </div>

        {/* Inspection Mode Toggles */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab("visual")}
            className={`px-2.5 py-1 rounded text-2xs font-mono font-medium transition-all ${
              activeTab === "visual"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            STANDARD
          </button>
          <button
            onClick={() => setActiveTab("uv")}
            className={`px-2.5 py-1 rounded text-2xs font-mono font-medium transition-all ${
              activeTab === "uv"
                ? "bg-purple-500/20 text-purple-300 border border-purple-500/30 shadow-[0_0_10px_rgba(168,85,247,0.2)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            TINT PREVIEW
          </button>
          <button
            onClick={() => setActiveTab("microtext")}
            className={`px-2.5 py-1 rounded text-2xs font-mono font-medium transition-all ${
              activeTab === "microtext"
                ? "bg-blue-500/20 text-blue-300 border border-blue-500/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            CONTRAST PREVIEW
          </button>
        </div>
      </div>

      {/* Main Recessed Scanner Inspection Area */}
      <div className="panel-recessed relative p-4 sm:p-6 h-[320px] sm:h-[380px] flex items-center justify-center overflow-hidden">
        {/* Recessed Corner Crosshair Brackets */}
        <div className="absolute top-2 left-2 font-mono text-xs text-slate-600">┼</div>
        <div className="absolute top-2 right-2 font-mono text-xs text-slate-600">┼</div>
        <div className="absolute bottom-2 left-2 font-mono text-xs text-slate-600">┼</div>
        <div className="absolute bottom-2 right-2 font-mono text-xs text-slate-600">┼</div>

        {/* Technical Grid Lines */}
        <div className="absolute inset-0 bg-tech-grid opacity-40 pointer-events-none" />

        {/* Moving Laser Sweep Line */}
        <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_20px_#10B981] animate-laser-sweep z-40 pointer-events-none" />

        {/* Illustrative Indian ₹500 banknote graphic */}
        <div
          className={`relative w-full max-w-[540px] aspect-[527/360] max-h-[260px] sm:max-h-[300px] flex items-center justify-center transition-all duration-500 ${
            activeTab === "uv"
              ? "brightness-115 contrast-125 hue-rotate-[240deg] shadow-[0_0_35px_rgba(168,85,247,0.3)]"
              : activeTab === "microtext"
              ? "scale-105 contrast-150 shadow-[0_0_35px_rgba(59,130,246,0.3)]"
              : "shadow-[0_0_30px_rgba(16,185,129,0.2)]"
          }`}
        >
          {/* Actual Indian ₹500 Banknote Image */}
          <img
            src="/inr_500_note.png"
            alt="Illustrative Indian 500 Rupee banknote"
            className="w-full h-full object-contain rounded drop-shadow-[0_10px_25px_rgba(0,0,0,0.8)]"
          />

          {/* 1. Security Thread Vertical Laser Alignment Line */}
          <div
            className={`absolute top-0 bottom-0 left-[48.6%] w-1 border-x transition-all duration-300 pointer-events-none z-20 ${
              activeTab === "uv"
                ? "bg-purple-400/90 border-purple-300 shadow-[0_0_15px_#A855F7]"
                : "bg-emerald-400/90 border-emerald-300 shadow-[0_0_15px_#10B981]"
            }`}
          >
            <span className="absolute top-3 left-1/2 -translate-x-1/2 text-[7px] font-mono font-extrabold text-emerald-200 tracking-tighter uppercase rotate-90">
              REFERENCE LINE
            </span>
          </div>

          {/* 2. Mahatma Gandhi Watermark Bounding Box */}
          <div className="absolute left-[36%] top-[12%] w-[26%] h-[76%] rounded border-2 border-dashed border-emerald-400/80 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.2)] pointer-events-none z-20">
            <span className="absolute -top-5 left-0 text-[8px] font-mono font-bold text-emerald-400 bg-slate-950/90 px-1.5 py-0.5 rounded border border-emerald-500/30">
              ILLUSTRATIVE REGION
            </span>
          </div>

          {/* 3. Serial Number Bounding Box */}
          <div className="absolute left-[8%] top-[18%] w-[28%] h-[24%] rounded border-2 border-emerald-400/80 bg-emerald-500/10 shadow-[0_0_12px_rgba(16,185,129,0.2)] pointer-events-none z-20">
            <span className="absolute -bottom-5 left-0 text-[8px] font-mono font-bold text-emerald-400 bg-slate-950/90 px-1.5 py-0.5 rounded border border-emerald-500/30">
              OCR SAMPLE: 5QB 814491
            </span>
          </div>

          {/* 4. Denomination Bounding Box */}
          <div className="absolute right-[8%] bottom-[16%] w-[24%] h-[26%] rounded border-2 border-emerald-400/80 bg-emerald-500/10 shadow-[0_0_12px_rgba(16,185,129,0.2)] pointer-events-none z-20">
            <span className="absolute -top-5 right-0 text-[8px] font-mono font-bold text-emerald-400 bg-slate-950/90 px-1.5 py-0.5 rounded border border-emerald-500/30">
              SAMPLE DENOM: ₹500
            </span>
          </div>

          {/* Dynamic Inspection Overlay Pin Badges */}
          <div className="absolute -top-3 right-0 z-30 flex items-center gap-1.5 bg-emerald-950/90 border border-emerald-500/60 px-2.5 py-1 rounded shadow-lg backdrop-blur-md">
            <span className="led-emerald led-emerald-pulse" />
            <span className="text-3xs font-mono font-bold text-emerald-300">REFERENCE OVERLAY</span>
          </div>

          <div className="absolute -bottom-3 left-0 z-30 flex items-center gap-1.5 bg-slate-950/95 border border-emerald-500/50 px-2.5 py-1 rounded shadow-lg backdrop-blur-md">
            <span className="led-emerald" />
            <span className="text-3xs font-mono font-bold text-slate-200">ILLUSTRATIVE REGION</span>
          </div>

          <div className="absolute -bottom-3 right-0 z-30 flex items-center gap-1.5 bg-slate-950/95 border border-blue-500/50 px-2.5 py-1 rounded shadow-lg backdrop-blur-md">
            <span className="h-2 w-2 rounded-full bg-blue-400 shadow-[0_0_6px_#3B82F6]" />
            <span className="text-3xs font-mono font-bold text-blue-200">SAMPLE SERIAL TEXT</span>
          </div>
        </div>
      </div>

      {/* Bottom Technical Readout Footer */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-2xs font-mono text-slate-400">
        <div className="flex items-center gap-4">
          <span>DEMO CLASS: <strong className="text-emerald-400">real_500 (illustrative)</strong></span>
          <span>LATENCY: <strong className="text-slate-200">not measured</strong></span>
        </div>
        <div>
          <span>SAMPLE ID: <strong className="text-slate-400 font-semibold">DEMO-0001</strong></span>
        </div>
      </div>
    </div>
  );
};
