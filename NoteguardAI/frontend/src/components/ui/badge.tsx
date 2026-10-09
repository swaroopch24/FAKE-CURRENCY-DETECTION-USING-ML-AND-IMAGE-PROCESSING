import React from "react";
import { cn } from "@/core/utils/cn";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "info";
}

export const Badge = ({ className, variant = "default", ...props }: BadgeProps) => {
  const base = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-all duration-200 hover:scale-105 select-none";
  
  const variants = {
    default: "bg-slate-800/80 text-slate-200 border border-slate-700 hover:border-slate-600 hover:shadow-[0_0_10px_rgba(255,255,255,0.05)]",
    success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:border-emerald-400/60 hover:shadow-[0_0_12px_rgba(16,185,129,0.2)]",
    warning: "bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:border-amber-400/60 hover:shadow-[0_0_12px_rgba(245,158,11,0.2)]",
    error: "bg-red-500/10 text-red-400 border border-red-500/30 hover:border-red-400/60 hover:shadow-[0_0_12px_rgba(239,68,68,0.2)]",
    info: "bg-blue-500/10 text-blue-400 border border-blue-500/30 hover:border-blue-400/60 hover:shadow-[0_0_12px_rgba(59,130,246,0.2)]"
  };

  return (
    <span className={cn(base, variants[variant], className)} {...props} />
  );
};
