import React from "react";
import { cn } from "@/core/utils/cn";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "outline" | "ghost" | "destructive" | "warning" | "tactilePrimary" | "tactileSecondary";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "md", isLoading, children, disabled, ...props }, ref) => {
    const baseStyle =
      "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none text-sm select-none";
    
    const variants = {
      default: "bg-emerald-600 hover:bg-emerald-500 text-white shadow-md hover:shadow-[0_0_20px_rgba(16,185,129,0.35)]",
      tactilePrimary: "btn-tactile-primary",
      tactileSecondary: "btn-tactile-secondary",
      secondary: "bg-slate-800 hover:bg-slate-700 text-white border border-slate-700/60 hover:border-slate-600 hover:shadow-[0_0_15px_rgba(255,255,255,0.05)]",
      outline: "border border-slate-700 hover:bg-slate-850 hover:border-emerald-500/40 text-slate-200 hover:shadow-[0_0_15px_rgba(16,185,129,0.1)]",
      ghost: "hover:bg-slate-800/70 text-slate-300 hover:text-slate-100",
      destructive: "bg-red-600 hover:bg-red-500 text-white shadow-md hover:shadow-[0_0_20px_rgba(239,68,68,0.35)]",
      warning: "bg-amber-600 hover:bg-amber-500 text-white shadow-md hover:shadow-[0_0_20px_rgba(245,158,11,0.35)]"
    };

    const sizes = {
      sm: "h-9 px-3 rounded-md text-xs",
      md: "h-10 px-4 py-2",
      lg: "h-11 px-8"
    };

    return (
      <button
        className={cn(baseStyle, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        ref={ref}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-transparent" />
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
