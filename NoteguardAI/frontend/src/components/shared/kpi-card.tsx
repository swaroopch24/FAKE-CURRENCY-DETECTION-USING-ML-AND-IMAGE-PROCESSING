import React from "react";
import { Card } from "@/components/ui/card";
import { cn } from "@/core/utils/cn";

export interface KPICardProps {
  title: string;
  value: React.ReactNode;
  change?: string;
  changeType?: "positive" | "negative" | "neutral" | "warning";
  icon?: React.ReactNode;
  className?: string;
}

export const KPICard = ({ title, value, change, changeType = "neutral", icon, className }: KPICardProps) => {
  const colorMap = {
    positive: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30 hover:border-emerald-400/60 hover:shadow-[0_0_10px_rgba(16,185,129,0.2)]",
    negative: "text-red-400 bg-red-500/10 border-red-500/30 hover:border-red-400/60 hover:shadow-[0_0_10px_rgba(239,68,68,0.2)]",
    neutral: "text-slate-400 bg-slate-800 border-slate-700 hover:border-slate-600",
    warning: "text-amber-400 bg-amber-500/10 border-amber-500/30 hover:border-amber-400/60 hover:shadow-[0_0_10px_rgba(245,158,11,0.2)]"
  };

  return (
    <Card className={cn("group p-6 flex flex-col justify-between min-h-[130px] cursor-pointer select-none transition-all duration-300", className)}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 group-hover:text-slate-400 transition-colors">{title}</span>
        {icon && <div className="text-slate-500 group-hover:text-emerald-400 group-hover:scale-110 transition-all duration-300">{icon}</div>}
      </div>

      <div className="flex items-baseline justify-between mt-auto">
        <span className="text-2xl font-bold tracking-tight text-slate-100 group-hover:text-white transition-colors">{value}</span>
        
        {change && (
          <span className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-2xs font-semibold border transition-all duration-200 hover:scale-105", colorMap[changeType])}>
            {change}
          </span>
        )}
      </div>
    </Card>
  );
};
