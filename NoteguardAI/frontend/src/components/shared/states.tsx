import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export const LoadingState = ({ message = "Screening Indian banknote image..." }: { message?: string }) => {
  const steps = [
    "Validating image format and dimensions...",
    "Running OCR safety and currency-eligibility checks...",
    "Running MobileNetV2 14-class classification...",
    "Checking authenticity and denomination confidence...",
    "Preparing the verification result..."
  ];

  const [stepIdx, setStepIdx] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIdx((prev) => (prev + 1) % steps.length);
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center select-none">
      {/* Dual Radar Ring Spinner */}
      <div className="relative mb-5 flex items-center justify-center">
        <div className="h-14 w-14 rounded-full border-2 border-emerald-500/20 border-t-emerald-400 animate-spin shadow-[0_0_20px_rgba(16,185,129,0.3)]" />
        <div className="absolute h-9 w-9 rounded-full border-2 border-emerald-400/30 border-b-emerald-400 animate-spin [animation-direction:reverse] [animation-duration:1.5s]" />
        <span className="absolute h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10B981] animate-ping" />
      </div>

      <span className="text-sm font-semibold font-mono text-slate-200">{message}</span>
      <span className="text-2xs font-mono text-emerald-400/90 mt-2 bg-slate-950 px-3 py-1 rounded border border-slate-800 transition-all duration-300">
        {steps[stepIdx]}
      </span>
    </div>
  );
};

export const EmptyState = ({
  title = "No Scan History Recorded",
  message = "Submit currency uploads via the Verification Studio to audit notes.",
  actionLabel,
  onAction
}: {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center border border-dashed border-slate-800 rounded-lg bg-slate-900/10">
      <svg className="h-12 w-12 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
      <h3 className="text-base font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-6">{message}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="default" size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export const ErrorState = ({
  title = "Authentication Check Failed",
  message = "An error occurred while communicating with the verification routers.",
  onRetry
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-red-950/20 bg-red-950/5 rounded-lg">
      <svg className="h-12 w-12 text-red-500/80 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <h3 className="text-base font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-6">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm">
          Retry Transaction
        </Button>
      )}
    </div>
  );
};
