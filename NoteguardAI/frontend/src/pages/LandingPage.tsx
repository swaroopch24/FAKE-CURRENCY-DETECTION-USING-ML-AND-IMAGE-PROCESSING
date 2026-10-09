import React, {
  useEffect, useRef, useState, useCallback, useMemo
} from "react";
import { Link } from "react-router-dom";
import { Shield, ArrowRight, Scan, CheckCircle, Cpu, Eye, FileSearch, Lock, Zap, Database } from "lucide-react";

// ════════════════════════════════════════════════════════════════════
// HOOKS
// ════════════════════════════════════════════════════════════════════

function useScrollProgress() {
  const [pct, setPct] = useState(0);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const handle = () => {
      const el = document.documentElement;
      const s = el.scrollTop || document.body.scrollTop;
      const total = el.scrollHeight - el.clientHeight;
      setPct(total > 0 ? Math.min(s / total, 1) : 0);
      setScrolled(s > 30);
    };
    window.addEventListener("scroll", handle, { passive: true });
    return () => window.removeEventListener("scroll", handle);
  }, []);
  return { pct, scrolled };
}

function useInView(threshold = 0.18) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { setVisible(true); obs.disconnect(); }
    }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, visible };
}

function useCountUp(target: number, active: boolean, duration = 1500, decimals = 0) {
  const [val, setVal] = useState(0);
  const [done, setDone] = useState(false);
  useEffect(() => {
    if (!active) return;
    setDone(false);
    const start = performance.now();
    let raf: number;
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      const cur = target * ease;
      setVal(decimals > 0 ? Math.round(cur * 10 ** decimals) / 10 ** decimals : Math.round(cur));
      if (t < 1) { raf = requestAnimationFrame(tick); }
      else { setVal(target); setDone(true); }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, target, duration, decimals]);
  return { val, done };
}

// ════════════════════════════════════════════════════════════════════
// BACKGROUND LAYERS
// ════════════════════════════════════════════════════════════════════

const PARTICLES = [
  { x: "8%",  y: "12%", size: 2, color: "#00d4ff", anim: "particle-float-1",  dur: "18s", delay: "0s"    },
  { x: "18%", y: "38%", size: 1.5, color: "#6366f1", anim: "particle-float-2", dur: "22s", delay: "-4s"   },
  { x: "82%", y: "15%", size: 2.5, color: "#00d4ff", anim: "particle-float-3", dur: "16s", delay: "-8s"   },
  { x: "75%", y: "55%", size: 1.5, color: "#8b5cf6", anim: "particle-float-4", dur: "24s", delay: "-2s"   },
  { x: "92%", y: "40%", size: 2,   color: "#00d4ff", anim: "particle-float-5", dur: "20s", delay: "-12s"  },
  { x: "35%", y: "78%", size: 1.5, color: "#6366f1", anim: "particle-float-6", dur: "19s", delay: "-6s"   },
  { x: "55%", y: "22%", size: 1,   color: "#00d4ff", anim: "particle-float-7", dur: "25s", delay: "-9s"   },
  { x: "12%", y: "65%", size: 2,   color: "#8b5cf6", anim: "particle-float-8", dur: "21s", delay: "-14s"  },
  { x: "65%", y: "85%", size: 1.5, color: "#00d4ff", anim: "particle-float-9", dur: "17s", delay: "-3s"   },
  { x: "45%", y: "48%", size: 1,   color: "#6366f1", anim: "particle-float-10","dur":"23s","delay":"-7s"  },
  { x: "88%", y: "72%", size: 2,   color: "#00d4ff", anim: "particle-float-11","dur":"20s","delay":"-11s" },
  { x: "28%", y: "92%", size: 1.5, color: "#8b5cf6", anim: "particle-float-12","dur":"26s","delay":"-5s"  },
];

function Background() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
      {/* Layer 1 — Base */}
      <div className="absolute inset-0 bg-[#070B14]" />

      {/* Layer 2 — Forensic grid */}
      <div className="absolute inset-0 forensic-grid opacity-100" />

      {/* Layer 3 — Atmospheric lighting */}
      <div className="absolute top-0 left-0 w-[60vw] h-[60vh] rounded-full"
           style={{ background: "radial-gradient(ellipse at 20% 20%, rgba(37,99,235,0.09) 0%, transparent 65%)" }} />
      <div className="absolute top-[10%] right-0 w-[50vw] h-[55vh] rounded-full"
           style={{ background: "radial-gradient(ellipse at 80% 15%, rgba(99,102,241,0.08) 0%, transparent 60%)" }} />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[70vw] h-[40vh]"
           style={{ background: "radial-gradient(ellipse at 50% 100%, rgba(0,212,255,0.05) 0%, transparent 55%)" }} />

      {/* Layer 4 — Forensic data particles */}
      {PARTICLES.map((p, i) => (
        <div
          key={i}
          className="absolute rounded-full"
          style={{
            left: p.x, top: p.y,
            width: p.size, height: p.size,
            background: p.color,
            boxShadow: `0 0 ${p.size * 3}px ${p.color}`,
            animation: `${p.anim} ${p.dur} ease-in-out infinite`,
            animationDelay: p.delay,
          }}
        />
      ))}

      {/* Layer 5 — HUD rings (behind hero) */}
      <div className="absolute top-[15%] left-[10%] w-[280px] h-[280px] opacity-[0.04]">
        <svg viewBox="0 0 280 280" className="w-full h-full hud-ring-cw">
          <circle cx="140" cy="140" r="130" fill="none" stroke="#00d4ff" strokeWidth="0.8" strokeDasharray="6 4" />
          <circle cx="140" cy="140" r="110" fill="none" stroke="#6366f1" strokeWidth="0.5" />
          <line x1="10" y1="140" x2="270" y2="140" stroke="#00d4ff" strokeWidth="0.4" />
          <line x1="140" y1="10" x2="140" y2="270" stroke="#00d4ff" strokeWidth="0.4" />
        </svg>
      </div>
      <div className="absolute bottom-[10%] right-[5%] w-[200px] h-[200px] opacity-[0.03]">
        <svg viewBox="0 0 200 200" className="w-full h-full hud-ring-ccw">
          <circle cx="100" cy="100" r="90"  fill="none" stroke="#8b5cf6" strokeWidth="0.8" strokeDasharray="4 6" />
          <circle cx="100" cy="100" r="70"  fill="none" stroke="#00d4ff" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="50"  fill="none" stroke="#6366f1" strokeWidth="0.3" />
        </svg>
      </div>

      {/* Layer 5b — Guilloché texture */}
      <div className="bg-guilloche absolute inset-0" />
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════
// HERO — FORENSIC SCANNER
// ════════════════════════════════════════════════════════════════════

function HeroScanner() {
  const [tab, setTab] = useState<"visual" | "uv" | "micro">("visual");
  const [gaugeVisible, setGaugeVisible] = useState(false);

  // Animate gauge ring after mount
  useEffect(() => {
    const t = setTimeout(() => setGaugeVisible(true), 600);
    return () => clearTimeout(t);
  }, []);

  // SVG circle gauge params
  const R = 54;
  const CIRC = 2 * Math.PI * R; // ~339.3
  const PCT = 0;
  const dash = gaugeVisible ? CIRC * PCT : 0;

  return (
    <div className="w-full max-w-6xl rounded-2xl overflow-hidden border border-slate-700/60 shadow-[0_25px_70px_-15px_rgba(0,0,0,0.9),0_0_50px_rgba(37,99,235,0.08)] bg-[#0A0F1D]/90 backdrop-blur-xl">

      {/* ─── TWO COLUMNS (SCANNER + GAUGE) ─────────────────────────── */}
      <div className="flex flex-col lg:flex-row items-stretch">

        {/* ══ LEFT — SCANNER PANEL ══════════════════════════════════ */}
        <div className="flex-1 flex flex-col border-b lg:border-b-0 lg:border-r border-slate-800/80 min-w-0">

          {/* Header row */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800/80 bg-slate-950/40">
            {/* Status */}
            <div className="flex items-center gap-3">
              <span className="led-emerald led-emerald-pulse flex-shrink-0" />
              <div>
                <div className="font-mono-data text-[10px] font-bold text-emerald-400 tracking-widest uppercase leading-tight">
                  SCANNER PREVIEW
                </div>
                <div className="font-mono-data text-[8px] text-slate-500 hidden sm:block">
                  Illustrative graphic only — no optical sensor or live scan.
                </div>
              </div>
            </div>

            {/* Mode tabs */}
            <div className="flex items-stretch bg-slate-950/90 border border-slate-700/70 rounded-lg p-0.5 shadow-inner">
              {(["visual", "uv", "micro"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setTab(m)}
                  className={`px-3.5 py-1.5 font-mono-data text-[9px] font-bold uppercase tracking-wider rounded-md transition-all ${
                    tab === m
                      ? m === "uv"
                        ? "bg-purple-500/25 text-purple-300 border border-purple-500/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                        : m === "micro"
                        ? "bg-blue-500/25 text-blue-300 border border-blue-500/40 shadow-[0_0_12px_rgba(59,130,246,0.3)]"
                        : "bg-emerald-500/25 text-emerald-300 border border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {m === "visual" ? "STANDARD" : m === "uv" ? "TINT PREVIEW" : "CONTRAST PREVIEW"}
                </button>
              ))}
            </div>
            <p className="mt-2 text-center text-[10px] text-slate-400">
              Illustrative graphic only; watermarks, security threads, and microtext are not individually verified.
            </p>
          </div>

          {/* Scanner viewport */}
          <div className="relative p-4 sm:p-6 flex-1 flex items-center justify-center overflow-hidden bg-[#040711]"
               style={{ minHeight: "360px", boxShadow: "inset 0 3px 20px rgba(0,0,0,0.95)" }}>

            {/* Background grid inside viewport */}
            <div className="absolute inset-0 bg-tech-grid opacity-30 pointer-events-none" />

            {/* Corner ┼ crosshair marks */}
            {(["top-3 left-3", "top-3 right-3", "bottom-3 left-3", "bottom-3 right-3"] as const).map((pos) => (
              <span key={pos} className={`absolute ${pos} font-mono-data text-xs leading-none select-none text-cyan-500/40`}>┼</span>
            ))}

            {/* Coordinate labels */}
            <span className="absolute top-4 left-8 font-mono-data text-[7px] text-cyan-500/30">X:0000_REF</span>
            <span className="absolute top-4 right-8 font-mono-data text-[7px] text-cyan-500/30">OPT_4K</span>
            <span className="absolute bottom-4 left-8 font-mono-data text-[7px] text-cyan-500/30">Y:0000_CAL</span>
            <span className="absolute bottom-4 right-8 font-mono-data text-[7px] text-cyan-500/30">1200_DPI</span>

            {/* Scanning laser line sweeping top-to-bottom */}
            <div
              className="absolute left-0 right-0 h-[3px] z-30 pointer-events-none animate-scanner-sweep"
              style={{
                background: "linear-gradient(90deg, transparent 0%, rgba(0,212,255,0.2) 10%, rgba(0,212,255,0.95) 50%, rgba(0,212,255,0.2) 90%, transparent 100%)",
                boxShadow: "0 0 10px 3px rgba(0,212,255,0.6), 0 0 25px rgba(0,212,255,0.25)",
              }}
            />

            {/* ── Banknote Presentation Box ── */}
            <div className="relative w-full max-w-[620px] aspect-[466/205] flex items-center justify-center rounded-lg shadow-[0_15px_35px_rgba(0,0,0,0.85)] border border-slate-700/50 overflow-hidden bg-slate-950">

              {/* Note Image */}
              <img
                src="/inr_500_cropped.png"
                alt="Illustrative ₹500 banknote graphic"
                className={`w-full h-full object-cover select-none transition-all duration-700 ${
                  tab === "uv"
                    ? "hue-rotate-[235deg] brightness-110 contrast-135"
                    : tab === "micro"
                    ? "contrast-150 brightness-95 scale-105"
                    : ""
                }`}
              />

              {/* Security thread vertical line at x = 55.4% */}
              <div
                className={`absolute top-0 bottom-0 left-[55.4%] w-[2px] z-20 pointer-events-none transition-colors duration-500 ${
                  tab === "uv"
                    ? "bg-purple-400 shadow-[0_0_12px_#a855f7]"
                    : "bg-emerald-400 shadow-[0_0_10px_#10b981]"
                }`}
              >
                <span className="absolute top-2 left-1/2 -translate-x-1/2 font-mono-data text-[6px] text-emerald-300 font-extrabold rotate-90 tracking-widest whitespace-nowrap drop-shadow">
                  REFERENCE LINE
                </span>
              </div>

              {/* Watermark area box (left Gandhi portrait watermark region) */}
              <div className="absolute left-[3%] top-[8%] w-[25%] h-[84%] border border-dashed border-emerald-400/60 rounded bg-emerald-500/10 z-20 pointer-events-none">
                <span className="absolute top-1 left-1.5 font-mono-data text-[7px] text-emerald-300 bg-slate-950/80 px-1 rounded border border-emerald-500/30">
                  ILLUSTRATIVE REGION
                </span>
                <span className="absolute bottom-1 left-1.5 font-mono-data text-[6px] text-emerald-300/80">
                  SAMPLE NOTE ART
                </span>
              </div>

              {/* Serial Number OCR Box (top-left) */}
              <div className="absolute left-[5%] top-[10%] w-[24%] h-[22%] border border-cyan-400/70 rounded bg-cyan-500/10 z-20 pointer-events-none">
                <span className="absolute -top-3 left-0 font-mono-data text-[6px] font-bold text-cyan-300 bg-slate-950/90 px-1 rounded border border-cyan-500/30">
                  OCR SAMPLE: 5QB 814491
                </span>
              </div>

              {/* Denomination Box (bottom-right ₹500) */}
              <div className="absolute right-[14%] bottom-[16%] w-[20%] h-[26%] border border-indigo-400/70 rounded bg-indigo-500/10 z-20 pointer-events-none">
                <span className="absolute -top-3 right-0 font-mono-data text-[6px] font-bold text-indigo-300 bg-slate-950/90 px-1 rounded border border-indigo-500/30">
                  SAMPLE DENOM: ₹500
                </span>
              </div>

              {/* Top Center Security Thread Detected Badge */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950/90 border border-emerald-500/60 font-mono-data text-[8px] sm:text-[9px] font-bold text-emerald-300 shadow-lg backdrop-blur-md">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10b981]" />
                REFERENCE OVERLAY
              </div>

              {/* Bottom Left Watermark Verified Badge */}
              <div className="marker-anim marker-d1 absolute bottom-2 left-2 z-30 flex items-center gap-1 px-2 py-0.5 rounded bg-slate-950/90 border border-emerald-500/50 font-mono-data text-[7px] sm:text-[8px] font-bold text-emerald-300 shadow-md backdrop-blur-md">
                <span className="w-1 h-1 rounded-full bg-emerald-400" />
                ILLUSTRATIVE REGION
              </div>

              {/* Bottom Right Microtext OK Badge */}
              <div className="marker-anim marker-d2 absolute bottom-2 right-2 z-30 flex items-center gap-1 px-2 py-0.5 rounded bg-slate-950/90 border border-blue-500/50 font-mono-data text-[7px] sm:text-[8px] font-bold text-blue-300 shadow-md backdrop-blur-md">
                <span className="w-1 h-1 rounded-full bg-blue-400 shadow-[0_0_4px_#3b82f6]" />
                SAMPLE TEXT REGION
              </div>
            </div>
          </div>

          {/* Footer row */}
          <div className="px-5 py-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between flex-wrap gap-x-6 gap-y-2">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="font-mono-data text-[10px] text-slate-400">
                DEMO CLASS: <strong className="text-emerald-400 font-bold">real_500 (illustrative)</strong>
              </span>
              <span className="font-mono-data text-[10px] text-slate-400">
                LATENCY: <strong className="text-slate-200 font-semibold">not measured</strong>
              </span>
            </div>
            <div className="font-mono-data text-[10px] text-slate-400">
              SAMPLE ID: <strong className="text-slate-300 font-mono">DEMO-0001</strong>
            </div>
          </div>
        </div>

        {/* ══ RIGHT — AI ANALYSIS GAUGE ═════════════════════════════ */}
        <div className="w-full lg:w-[320px] flex flex-col bg-slate-950/30">

          {/* Panel header */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800/80 bg-slate-950/50">
            <div className="flex items-center gap-2">
              <span className="led-emerald led-emerald-pulse" />
              <span className="font-mono-data text-[10px] font-bold text-slate-200 tracking-widest uppercase">
                ILLUSTRATIVE PREVIEW
              </span>
            </div>
            <span className="font-mono-data text-[8px] px-2 py-0.5 rounded font-bold bg-emerald-500/15 border border-emerald-500/40 text-emerald-300">
              DEMO ONLY
            </span>
          </div>

          {/* Circular gauge */}
          <div className="flex-1 flex flex-col items-center justify-center p-6">
            <div className="relative w-40 h-40 mb-6">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
                {/* Track */}
                <circle cx="64" cy="64" r={R} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="9" />
                {/* Progress arc */}
                <circle
                  cx="64" cy="64" r={R}
                  fill="none"
                  stroke="url(#gaugeGrad)"
                  strokeWidth="9"
                  strokeLinecap="round"
                  strokeDasharray={`${CIRC}`}
                  strokeDashoffset={CIRC - dash}
                  style={{
                    transition: "stroke-dashoffset 1.8s cubic-bezier(0.16,1,0.3,1) 0.6s",
                    filter: "drop-shadow(0 0 8px rgba(16,185,129,0.8))",
                  }}
                />
                <defs>
                  <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#10b981" />
                  </linearGradient>
                </defs>
              </svg>
              {/* Center label */}
              <div className="absolute inset-0 flex flex-col items-center justify-center select-none">
                <span className="font-mono-data text-3xl font-black text-emerald-400 leading-none tracking-tight">
                  --
                </span>
                <span className="font-mono-data text-[9px] font-extrabold text-emerald-400 tracking-[0.2em] uppercase mt-1.5">
                  EXAMPLE
                </span>
              </div>
            </div>

            {/* Data telemetry rows */}
            <div className="w-full space-y-2.5">
              {[
                { label: "OCR SAFETY",       val: "RULE SCREENING",    color: "#34d399", bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.2)" },
                { label: "CLASSIFIER",       val: "MobileNetV2 · 14 classes", color: "#60a5fa", bg: "rgba(59,130,246,0.08)", border: "rgba(59,130,246,0.2)" },
                { label: "DECISION POLICY",  val: "BOTH SCORES ≥ 80%", color: "#c084fc", bg: "rgba(168,85,247,0.08)", border: "rgba(168,85,247,0.2)" },
              ].map((row) => (
                <div
                  key={row.label}
                  className="flex items-center justify-between px-3.5 py-2.5 rounded-lg border transition-all hover:translate-x-0.5"
                  style={{ background: row.bg, borderColor: row.border }}
                >
                  <span className="font-mono-data text-[8px] text-slate-400 tracking-wider uppercase font-semibold">
                    {row.label}
                  </span>
                  <span className="font-mono-data text-[10px] font-bold" style={{ color: row.color }}>
                    {row.val}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}


// ════════════════════════════════════════════════════════════════════
// TECHNICAL READOUTS (right column)
// ════════════════════════════════════════════════════════════════════

const READOUTS = [
  { key: "MODEL",      val: "MobileNetV2", color: "text-blue-400"    },
  { key: "VISION",     val: "OpenCV",      color: "text-cyan-400"    },
  { key: "PROCESSING", val: "REAL-TIME",   color: "text-emerald-400" },
  { key: "ACCURACY",   val: "98.65%",      color: "text-indigo-400"  },
];

function TechnicalReadout() {
  return (
    <div className="flex flex-col gap-3">
      {READOUTS.map((r, i) => (
        <div key={r.key}
             className={`hero-anim hero-d${i + 4} panel-raised px-4 py-3 rounded-xl`}
             style={{ minWidth: 140 }}>
          <span className="block font-mono-data text-[8px] text-slate-500 tracking-widest uppercase mb-1">{r.key}</span>
          <span className={`font-mono-data text-sm font-bold ${r.color}`}>{r.val}</span>
        </div>
      ))}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════
// STAT CARD
// ════════════════════════════════════════════════════════════════════

function StatCard({ label, target, suffix, isText, textVal, color, active }: {
  label: string; target: number; suffix?: string; isText?: boolean; textVal?: string; color: string; active: boolean;
}) {
  const { val, done } = useCountUp(target, active && !isText, 1400, suffix === "%" ? 2 : 0);
  const display = isText ? textVal! : `${val}${suffix ?? ""}`;
  return (
    <div className="panel-raised px-5 py-4 rounded-xl text-center hover:-translate-y-0.5 transition-all duration-200 hover:shadow-[0_8px_24px_rgba(59,130,246,0.1)]">
      <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">{label}</span>
      <span className={`font-mono-data text-xl font-black ${color} ${active && !done && !isText ? "counting" : ""}`}>{display}</span>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════
// WORKFLOW SECTION
// ════════════════════════════════════════════════════════════════════

const WORKFLOW = [
  { num: "01", title: "Upload Image",        desc: "Upload JPG/PNG banknote or capture via live camera.", color: "#3b82f6", bg: "rgba(59,130,246,0.12)", border: "rgba(59,130,246,0.3)" },
  { num: "02", title: "Image Validation",    desc: "Check image format, file size, and minimum image dimensions.", color: "#00d4ff", bg: "rgba(0,212,255,0.10)",  border: "rgba(0,212,255,0.3)" },
  { num: "03", title: "OCR Safety & Eligibility", desc: "Screen explicit counterfeit markers and look for Indian-currency evidence before CNN inference.", color: "#8b5cf6", bg: "rgba(139,92,246,0.1)", border: "rgba(139,92,246,0.3)" },
  { num: "04", title: "AI Classification",   desc: "MobileNetV2 CNN evaluates authenticity across classes.", color: "#a855f7", bg: "rgba(168,85,247,0.10)", border: "rgba(168,85,247,0.3)" },
  { num: "05", title: "Confidence Policy",   desc: "Require both authenticity and denomination confidence to meet the configured threshold.", color: "#06b6d4", bg: "rgba(6,182,212,0.10)", border: "rgba(6,182,212,0.3)" },
  { num: "06", title: "Verification Result", desc: "Return a classification, unsupported-currency response, or an uncertain result.", color: "#10b981", bg: "rgba(16,185,129,0.10)", border: "rgba(16,185,129,0.3)" },
];

function WorkflowSection() {
  const { ref, visible } = useInView(0.12);
  return (
    <section ref={ref as React.RefObject<HTMLElement>} className="relative z-10 max-w-6xl mx-auto px-6 py-24">
      {/* heading */}
      <div className={`text-center mb-16 reveal-init ${visible ? "reveal-active" : ""}`}>
        <span className="inline-block px-3 py-1 rounded-full bg-blue-600/15 border border-blue-500/25 font-mono-data text-[9px] text-blue-400 tracking-widest uppercase mb-4">
          FORENSIC PIPELINE
        </span>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-100 mb-3">
          How NoteGuard Analyzes a Banknote
        </h2>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          End-to-end AI verification pipeline — from image capture to authenticated verdict.
        </p>
      </div>

      {/* Mobile (vertical) */}
      <div className="flex flex-col items-center gap-0 md:hidden">
        {WORKFLOW.map((step, i) => (
          <React.Fragment key={step.num}>
            <div className={`w-full max-w-sm reveal-init ${visible ? "reveal-active" : ""}`}
                 style={{ transitionDelay: `${i * 100}ms` }}>
              <div className="panel-raised p-5 rounded-xl module-card border"
                   style={{ borderColor: step.border }}>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center font-mono-data text-xs font-black flex-shrink-0"
                       style={{ background: step.bg, border: `1px solid ${step.border}`, color: step.color }}>
                    {step.num}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100 mb-1">{step.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
                  </div>
                </div>
              </div>
            </div>
            {i < WORKFLOW.length - 1 && (
              <div className="flex flex-col items-center my-1">
                <div className={`pipeline-connector-v ${visible ? "pipe-active" : ""}`}
                     style={{ transitionDelay: `${i * 100 + 200}ms`, minHeight: 28 }} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Desktop (2-column grid with connectors) */}
      <div className="hidden md:grid grid-cols-3 gap-x-4 gap-y-6">
        {WORKFLOW.map((step, i) => (
          <div key={step.num}
               className={`reveal-init ${visible ? "reveal-active" : ""}`}
               style={{ transitionDelay: `${i * 100}ms` }}>
            <div className="panel-raised p-6 rounded-xl h-full module-card border"
                 style={{ borderColor: "rgba(255,255,255,0.06)" }}>
              {/* number badge */}
              <div className="w-10 h-10 rounded-xl flex items-center justify-center font-mono-data text-sm font-black mb-4"
                   style={{ background: step.bg, border: `1px solid ${step.border}`, color: step.color }}>
                {step.num}
              </div>
              <h3 className="text-sm font-bold text-slate-100 mb-2">{step.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
              {/* inline connector tag */}
              <div className="mt-3 pt-3 border-t border-slate-800/50">
                <span className="font-mono-data text-[8px] tracking-widest uppercase" style={{ color: step.color }}>
                  STAGE {step.num} / 06
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline flow line (desktop) */}
      <div className="hidden md:flex items-center gap-2 mt-8 px-2">
        {WORKFLOW.map((step, i) => (
          <React.Fragment key={step.num}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center font-mono-data text-[9px] font-bold flex-shrink-0"
                 style={{ background: step.bg, border: `1px solid ${step.border}`, color: step.color }}>
              {step.num}
            </div>
            {i < WORKFLOW.length - 1 && (
              <div className={`pipeline-connector ${visible ? "pipe-active" : ""}`}
                   style={{ transitionDelay: `${i * 200 + 300}ms` }} />
            )}
          </React.Fragment>
        ))}
      </div>
    </section>
  );
}

// ════════════════════════════════════════════════════════════════════
// FORENSIC MODULES SECTION
// ════════════════════════════════════════════════════════════════════

const MODULES = [
  {
    icon: <Shield className="w-6 h-6" />,
    title: "Authenticity Detection",
    desc: "AI-powered binary classification — genuine or counterfeit — with confidence scoring.",
    color: "#10b981", bg: "rgba(16,185,129,0.12)", border: "rgba(16,185,129,0.25)",
    tag: "CNN · BINARY"
  },
  {
    icon: <Eye className="w-6 h-6" />,
    title: "OCR Safety & Eligibility",
    desc: "Screen explicit counterfeit markers and strong foreign-currency text before classification.",
    color: "#3b82f6", bg: "rgba(59,130,246,0.12)", border: "rgba(59,130,246,0.25)",
    tag: "OCR · RULES"
  },
  {
    icon: <Scan className="w-6 h-6" />,
    title: "Image Validation",
    desc: "Validate image format, file size, readability, and minimum dimensions.",
    color: "#00d4ff", bg: "rgba(0,212,255,0.10)", border: "rgba(0,212,255,0.25)",
    tag: "INPUT · IMAGE"
  },
  {
    icon: <Cpu className="w-6 h-6" />,
    title: "Deep Learning Engine",
    desc: "MobileNetV2 classifies supported Indian-note authenticity and denomination classes.",
    color: "#8b5cf6", bg: "rgba(139,92,246,0.12)", border: "rgba(139,92,246,0.25)",
    tag: "MOBILENETV2 · CNN"
  },
  {
    icon: <FileSearch className="w-6 h-6" />,
    title: "Image Processing",
    desc: "Resize the validated RGB image to the CNN input size using bilinear interpolation.",
    color: "#a855f7", bg: "rgba(168,85,247,0.12)", border: "rgba(168,85,247,0.25)",
    tag: "PREPROCESSING"
  },
  {
    icon: <Database className="w-6 h-6" />,
    title: "Verification Reports",
    desc: "Return the classification, confidence scores, decision reason, and processing metadata.",
    color: "#06b6d4", bg: "rgba(6,182,212,0.12)", border: "rgba(6,182,212,0.25)",
    tag: "AUDIT · PDF"
  },
];

function ForensicModules() {
  const { ref, visible } = useInView(0.1);
  return (
    <section ref={ref as React.RefObject<HTMLElement>} className="relative z-10 max-w-6xl mx-auto px-6 py-20">
      <div className={`text-center mb-14 reveal-init ${visible ? "reveal-active" : ""}`}>
        <span className="inline-block px-3 py-1 rounded-full bg-indigo-600/15 border border-indigo-500/25 font-mono-data text-[9px] text-indigo-400 tracking-widest uppercase mb-4">
          VERIFICATION PIPELINE
        </span>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-100 mb-3">
          Verification Modules
        </h2>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          Image screening, OCR safety rules, and confidence-gated CNN classification.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {MODULES.map((m, i) => (
          <div key={m.title}
               className={`panel-raised p-6 rounded-xl module-card reveal-init ${visible ? "reveal-active" : ""}`}
               style={{ borderColor: "rgba(255,255,255,0.06)", transitionDelay: `${i * 80}ms` }}>
            {/* icon */}
            <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                 style={{ background: m.bg, border: `1px solid ${m.border}`, color: m.color }}>
              {m.icon}
            </div>
            <h3 className="text-sm font-bold text-slate-100 mb-2">{m.title}</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">{m.desc}</p>
            <span className="font-mono-data text-[8px] px-2 py-0.5 rounded border tracking-widest uppercase"
                  style={{ color: m.color, background: m.bg, borderColor: m.border }}>
              {m.tag}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

// ════════════════════════════════════════════════════════════════════
// DETECTION ENGINE PIPELINE
// ════════════════════════════════════════════════════════════════════

const ENGINE_STEPS = [
  { label: "VALIDATE IMAGE", color: "#64748b" },
  { label: "OCR SAFETY", color: "#00d4ff" },
  { label: "CURRENCY ELIGIBILITY", color: "#3b82f6" },
  { label: "BILINEAR RESIZE", color: "#8b5cf6" },
  { label: "MOBILENETV2", color: "#a855f7" },
  { label: "DUAL THRESHOLD", color: "#06b6d4" },
  { label: "RESULT", color: "#10b981" },
];

function DetectionEngine() {
  const { ref, visible } = useInView(0.15);
  return (
    <section ref={ref as React.RefObject<HTMLElement>} className="relative z-10 max-w-6xl mx-auto px-6 py-20">
      <div className={`text-center mb-14 reveal-init ${visible ? "reveal-active" : ""}`}>
        <span className="inline-block px-3 py-1 rounded-full bg-cyan-600/15 border border-cyan-500/25 font-mono-data text-[9px] text-cyan-400 tracking-widest uppercase mb-4">
          TECHNOLOGY STACK
        </span>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-100 mb-3">
          Verification Pipeline
        </h2>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          OCR safety and eligibility checks run before CNN classification and decision thresholds.
        </p>
      </div>

      {/* Desktop horizontal pipeline */}
      <div className={`hidden md:flex items-center gap-0 reveal-init ${visible ? "reveal-active" : ""}`}
           style={{ transitionDelay: "150ms" }}>
        {ENGINE_STEPS.map((step, i) => (
          <React.Fragment key={step.label}>
            <div className="flex flex-col items-center gap-2 flex-shrink-0">
              <div className="panel-raised px-3 py-2.5 rounded-xl text-center"
                   style={{ border: `1px solid ${step.color}30` }}>
                <div className="w-2 h-2 rounded-full mx-auto mb-2" style={{ background: step.color, boxShadow: `0 0 8px ${step.color}` }} />
                <span className="font-mono-data text-[8px] font-bold tracking-widest" style={{ color: step.color }}>
                  {step.label}
                </span>
              </div>
            </div>
            {i < ENGINE_STEPS.length - 1 && (
              <div className={`pipeline-connector mx-1 ${visible ? "pipe-active" : ""}`}
                   style={{ transitionDelay: `${i * 150 + 200}ms`, minWidth: 32 }} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Mobile vertical */}
      <div className="flex md:hidden flex-col items-center gap-1">
        {ENGINE_STEPS.map((step, i) => (
          <React.Fragment key={step.label}>
            <div className={`panel-raised px-5 py-3 rounded-xl w-full max-w-xs reveal-init ${visible ? "reveal-active" : ""}`}
                 style={{ borderColor: `${step.color}25`, transitionDelay: `${i * 80}ms` }}>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: step.color, boxShadow: `0 0 6px ${step.color}` }} />
                <span className="font-mono-data text-xs font-bold" style={{ color: step.color }}>{step.label}</span>
              </div>
            </div>
            {i < ENGINE_STEPS.length - 1 && (
              <div className={`pipeline-connector-v ${visible ? "pipe-active" : ""}`}
                   style={{ transitionDelay: `${i * 100 + 150}ms`, minHeight: 24 }} />
            )}
          </React.Fragment>
        ))}
      </div>
    </section>
  );
}

// ════════════════════════════════════════════════════════════════════
// TRUST / SECURITY SECTION
// ════════════════════════════════════════════════════════════════════

const TRUST_ITEMS = [
  { label: "AI-Powered Analysis",          sub: "MobileNetV2 deep learning classification", color: "#10b981" },
  { label: "Image Validation",             sub: "Format, size, readability, and dimensions", color: "#3b82f6" },
  { label: "OCR Safety & Eligibility",     sub: "Text rules run before CNN classification", color: "#8b5cf6" },
  { label: "Dual Confidence Policy",        sub: "Authenticity and denomination thresholds", color: "#00d4ff" },
  { label: "Decision Reasons",             sub: "Status and policy outcome returned per scan", color: "#06b6d4" },
  { label: "Indian Currency Scope",        sub: "Eligibility checks target Indian banknotes", color: "#a855f7" },
];

function TrustSection() {
  const { ref, visible } = useInView(0.12);
  return (
    <section ref={ref as React.RefObject<HTMLElement>} className="relative z-10 max-w-6xl mx-auto px-6 py-20">
      <div className={`text-center mb-14 reveal-init ${visible ? "reveal-active" : ""}`}>
        <span className="inline-block px-3 py-1 rounded-full bg-emerald-600/15 border border-emerald-500/25 font-mono-data text-[9px] text-emerald-400 tracking-widest uppercase mb-4">
          SYSTEM CAPABILITIES
        </span>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-100 mb-3">
          Built for Precision &amp; Trust
        </h2>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          NoteGuard screens Indian banknote images and reports model classifications with conservative decision thresholds.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {TRUST_ITEMS.map((item, i) => (
          <div key={item.label}
               className={`panel-raised p-5 rounded-xl flex items-start gap-4 module-card reveal-init ${visible ? "reveal-active" : ""}`}
               style={{ transitionDelay: `${i * 80}ms`, borderColor: "rgba(255,255,255,0.06)" }}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                 style={{ background: `${item.color}18`, border: `1px solid ${item.color}35` }}>
              <CheckCircle className="w-4 h-4" style={{ color: item.color }} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100 mb-1">{item.label}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{item.sub}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ════════════════════════════════════════════════════════════════════
// FINAL CTA STRIP
// ════════════════════════════════════════════════════════════════════

function CtaStrip() {
  const { ref, visible } = useInView(0.2);
  return (
    <section ref={ref as React.RefObject<HTMLElement>}
             className={`relative z-10 max-w-4xl mx-auto px-6 py-20 text-center reveal-init ${visible ? "reveal-active" : ""}`}>
      <div className="panel-raised rounded-2xl p-12 relative overflow-hidden"
           style={{ boxShadow: "inset 0 1px 0 rgba(255,255,255,0.08), 0 20px 60px -10px rgba(0,0,0,0.7), 0 0 40px rgba(37,99,235,0.06)" }}>
        {/* BG accent */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-48 rounded-full blur-[80px]"
             style={{ background: "radial-gradient(ellipse, rgba(37,99,235,0.12) 0%, transparent 70%)" }} />
        <div className="relative z-10">
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="led-emerald led-emerald-pulse" />
            <span className="font-mono-data text-[9px] text-emerald-400 tracking-widest uppercase font-semibold">System Ready</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-slate-100 mb-4 leading-tight">
            Start Verifying Currency<br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400">
              with AI Precision
            </span>
          </h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto mb-10 leading-relaxed">
            Access the forensic scanner, review results, and generate authenticated audit reports.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link to="/login">
              <button className="cta-primary px-10 py-3.5 rounded-xl text-sm font-bold flex items-center gap-2">
                <Zap className="w-4 h-4" />
                START VERIFICATION
              </button>
            </Link>
            <Link to="/login">
              <button className="cta-secondary px-8 py-3.5 rounded-xl text-sm font-semibold">
                View Dashboard
              </button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

// ════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════════════════

const STATS = [
  { label: "AI Accuracy",     target: 98.65, suffix: "%",  decimals: 2, color: "text-blue-400",    isText: false },
  { label: "Deep Learning",   target: 0,     suffix: "",   decimals: 0, color: "text-cyan-400",    isText: true, textVal: "MobileNetV2" },
  { label: "Detection Speed", target: 2,     suffix: "s",  decimals: 0, color: "text-indigo-400",  isText: true, textVal: "< 2 Seconds" },
  { label: "System Security", target: 100,   suffix: "% Safe", decimals: 0, color: "text-emerald-400", isText: true, textVal: "100% Safe" },
];

export default function LandingPage() {
  const { pct, scrolled } = useScrollProgress();
  const { ref: statsRef, visible: statsVisible } = useInView(0.3);

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col relative overflow-x-hidden selection:bg-blue-500/30 selection:text-blue-200">

      {/* Background (fixed, all layers) */}
      <Background />

      {/* Security thread progress indicator */}
      <div className="security-thread" style={{ "--scroll-pct": `${pct * 100}%` } as React.CSSProperties} />

      {/* ─── HEADER ─────────────────────────────────────────────────── */}
      <header className={`sticky top-0 z-50 border-b border-slate-800/50 transition-all duration-300 ${
        scrolled ? "bg-[#070B14]/92 backdrop-blur-xl shadow-[0_1px_24px_rgba(0,0,0,0.6)]" : "bg-transparent"
      }`}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30 flex-shrink-0">
              <Shield className="h-5 w-5 fill-current text-white" />
            </div>
            <div>
              <span className="font-extrabold tracking-wider text-slate-100 text-base leading-none block">FCD SYSTEM</span>
              <span className="font-mono-data text-[8px] text-blue-400 tracking-widest uppercase">Fake Currency Detection</span>
            </div>
          </div>
          <nav className="flex items-center gap-5">
            <a href="#how-it-works" className="hidden sm:block text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors">
              How It Works
            </a>
            <a href="#modules" className="hidden sm:block text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors">
              Modules
            </a>
            <Link to="/login">
              <button className="cta-primary px-5 py-2 rounded-lg text-xs font-bold">
                Sign In
              </button>
            </Link>
          </nav>
        </div>
      </header>

      {/* ─── HERO ────────────────────────────────────────────────────── */}
      <main className="relative z-10 flex-1">
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 flex flex-col items-center">

          {/* Status pill — centered */}
          <div className="flex justify-center mb-8">
            <div className="hero-anim hero-d0 inline-flex items-center gap-3 px-4 py-2 rounded-full border shadow-sm"
                 style={{ background: "rgba(16,185,129,0.08)", borderColor: "rgba(16,185,129,0.25)" }}>
              <span className="led-emerald led-emerald-pulse" />
              <span className="font-mono-data text-[9px] font-semibold text-emerald-400 tracking-widest uppercase">
                AI Verification Engine · Online
              </span>
              <span className="w-px h-3 bg-slate-700" />
              <span className="font-mono-data text-[9px] text-slate-400">v2.4.1-stable</span>
            </div>
          </div>

          {/* ── Centered headline block ── */}
          <div className="text-center max-w-3xl mx-auto">

            {/* Eyebrow */}
            <div className="hero-anim hero-d1 flex justify-center mb-4">
              <span className="font-mono-data text-[10px] text-blue-400 tracking-[0.25em] uppercase font-bold">
                AI-POWERED BANKNOTE FORENSICS
              </span>
            </div>

            {/* H1 */}
            <h1 className="hero-anim hero-d2 font-black leading-[1.05] tracking-tight mb-5">
              <span className="block text-4xl sm:text-5xl lg:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-blue-100 to-slate-200">
                Real-Time Fake
              </span>
              <span className="block text-4xl sm:text-5xl lg:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400">
                Currency
              </span>
              <span className="block text-4xl sm:text-5xl lg:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-blue-100 to-slate-200">
                Detection
              </span>
            </h1>

            {/* Subtitle */}
            <p className="hero-anim hero-d3 text-slate-400 text-base sm:text-lg leading-relaxed max-w-2xl mx-auto mb-8">
              Screen Indian banknote images with OCR safety rules and MobileNetV2 classification for authenticity and denomination.
            </p>

            {/* CTAs — centered */}
            <div className="hero-anim hero-d4 flex flex-wrap items-center justify-center gap-4 mb-12">
              <Link to="/login">
                <button className="cta-primary px-9 py-3.5 rounded-xl text-sm font-bold flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Start Verification
                </button>
              </Link>
              <a href="#how-it-works">
                <button className="cta-secondary px-8 py-3.5 rounded-xl text-sm font-semibold flex items-center gap-2">
                  Explore Technology
                  <ArrowRight className="w-4 h-4" />
                </button>
              </a>
            </div>
          </div>

          {/* ── Scanner — centered full width (max-w-6xl) ── */}
          <div className="hero-anim hero-d5 w-full flex justify-center mb-8">
            <HeroScanner />
          </div>

          {/* ── Stats 4-column row — aligned with scanner width ── */}
          <div ref={statsRef as React.RefObject<HTMLDivElement>}
               className="hero-anim hero-d6 grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-6xl mb-4">
            {STATS.map((s) => (
              <StatCard key={s.label} {...s} active={statsVisible} />
            ))}
          </div>

          {/* ── Technical readouts — aligned with scanner width ── */}
          <div className="hero-anim hero-d7 hidden sm:grid grid-cols-4 gap-3 w-full max-w-6xl">
            {READOUTS.map((r) => (
              <div key={r.key}
                   className="panel-raised px-4 py-3 rounded-xl flex flex-col items-center text-center">
                <span className="font-mono-data text-[7px] text-slate-500 tracking-widest uppercase mb-1">{r.key}</span>
                <span className={`font-mono-data text-sm font-bold ${r.color}`}>{r.val}</span>
              </div>
            ))}
          </div>

        </section>


        {/* ─── HOW IT WORKS ────────────────────────────────────────── */}
        <div id="how-it-works">
          <WorkflowSection />
        </div>

        {/* ─── FORENSIC MODULES ────────────────────────────────────── */}
        <div id="modules">
          <ForensicModules />
        </div>

        {/* ─── DETECTION ENGINE ────────────────────────────────────── */}
        <DetectionEngine />

        {/* ─── TRUST SECTION ───────────────────────────────────────── */}
        <TrustSection />

        {/* ─── FINAL CTA ───────────────────────────────────────────── */}
        <CtaStrip />
      </main>

      {/* ─── FOOTER ──────────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-slate-900/80 py-8 bg-[#070B14]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <Shield className="h-4 w-4 fill-current text-white" />
            </div>
            <span className="font-mono-data text-[10px] text-slate-500">FCD SYSTEM — AI BANKNOTE FORENSICS</span>
          </div>
          <span className="font-mono-data text-[10px] text-slate-600">
            &copy; {new Date().getFullYear()} FCD System · All Rights Reserved
          </span>
        </div>
      </footer>
    </div>
  );
}
