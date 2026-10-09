import React from "react";
import { cn } from "@/core/utils/cn";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  options: { value: string | number; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, options, ...props }, ref) => {
    return (
      <div className="w-full">
        <select
          className={cn(
            "flex h-10 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 transition-colors focus:border-emerald-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500 focus:border-red-500",
            className
          )}
          ref={ref}
          {...props}
        >
          {options.map(opt => (
            <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-100">
              {opt.label}
            </option>
          ))}
        </select>
        {error && <span className="text-xs text-red-500 mt-1 block">{error}</span>}
      </div>
    );
  }
);

Select.displayName = "Select";
