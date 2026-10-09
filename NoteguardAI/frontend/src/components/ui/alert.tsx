import React from "react";
import { cn } from "@/core/utils/cn";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "warning" | "destructive";
  title?: string;
}

export const Alert = ({ className, variant = "default", title, children, ...props }: AlertProps) => {
  const base = "relative w-full rounded-lg border p-4 text-sm backdrop-blur-md";
  
  const variants = {
    default: "bg-slate-900 border-slate-800 text-slate-300",
    success: "bg-emerald-950/20 border-emerald-800/30 text-emerald-300",
    warning: "bg-amber-950/20 border-amber-800/30 text-amber-300",
    destructive: "bg-red-950/20 border-red-800/30 text-red-300"
  };

  return (
    <div className={cn(base, variants[variant], className)} role="alert" {...props}>
      {title && <h5 className="font-semibold leading-none tracking-tight mb-1 text-slate-100">{title}</h5>}
      <div className="text-xs leading-relaxed opacity-90">{children}</div>
    </div>
  );
};
