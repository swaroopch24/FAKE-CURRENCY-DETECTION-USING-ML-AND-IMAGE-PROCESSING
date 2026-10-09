import React from "react";
import { cn } from "@/core/utils/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "raised" | "recessed";
  hoverGlow?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "raised", hoverGlow = true, children, ...props }, ref) => {
    return (
      <div
        className={cn(
          variant === "raised" ? "panel-raised p-6 text-slate-100" : "panel-recessed p-6 text-slate-100",
          hoverGlow && variant === "raised" && "hover:border-emerald-500/40 hover:shadow-[0_15px_35px_-10px_rgba(16,185,129,0.15)]",
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";
