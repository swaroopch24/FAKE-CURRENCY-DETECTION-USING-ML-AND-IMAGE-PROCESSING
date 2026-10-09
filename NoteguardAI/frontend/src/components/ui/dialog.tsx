"use client";

import React from "react";
import { cn } from "@/core/utils/cn";
import { Button } from "@/components/ui/button";

export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footerActions?: React.ReactNode;
}

export const Dialog = ({ isOpen, onClose, title, children, footerActions }: DialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      
      {/* Dialog Content */}
      <div className="relative w-full max-w-lg rounded-lg border border-slate-800 bg-slate-900 p-6 text-slate-100 shadow-lg animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 transition-colors">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Body */}
        <div className="text-sm text-slate-300 leading-relaxed mb-6">
          {children}
        </div>
        
        {/* Footer */}
        {footerActions && (
          <div className="flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
            {footerActions}
          </div>
        )}
      </div>
    </div>
  );
};
