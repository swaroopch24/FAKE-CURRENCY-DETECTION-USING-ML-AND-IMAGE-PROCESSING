import React from "react";
import { cn } from "@/core/utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", error, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500 focus:border-red-500",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <span className="text-xs text-red-500 mt-1 block">{error}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";
