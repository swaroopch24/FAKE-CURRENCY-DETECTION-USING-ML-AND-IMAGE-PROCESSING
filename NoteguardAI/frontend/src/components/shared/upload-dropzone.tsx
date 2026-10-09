"use client";

import React, { useState, useRef } from "react";
import { cn } from "@/core/utils/cn";
import { Button } from "@/components/ui/button";

export interface UploadDropzoneProps {
  label: string;
  onFileSelect: (file: File) => void;
  onClear?: () => void;
  error?: string;
}

export const UploadDropzone = ({ label, onFileSelect, onClear, error }: UploadDropzoneProps) => {
  const [dragOver, setDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragOver(true);
    } else {
      setDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    // Basic format filter
    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      alert("Invalid format. Please upload JPG, PNG, or WEBP.");
      return;
    }

    // Set preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Call state hook
    onFileSelect(file);
  };

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (onClear) onClear();
  };

  return (
    <div
      onClick={() => fileInputRef.current?.click()}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "relative flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-6 cursor-pointer transition-all duration-300 w-full min-h-[220px] select-none",
        dragOver
          ? "border-emerald-400 bg-emerald-500/10 scale-[1.01] shadow-[0_0_25px_rgba(16,185,129,0.25)]"
          : "border-slate-800 bg-slate-900/10 hover:border-slate-700/80 hover:bg-slate-900/30 hover:scale-[1.005]",
        error ? "border-red-500/80 bg-red-500/10" : ""
      )}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInput}
        accept=".jpg,.jpeg,.png,.webp"
        className="hidden"
      />

      {previewUrl ? (
        <div className="relative w-full h-[180px] flex items-center justify-center overflow-hidden rounded-md animate-in fade-in zoom-in-95 duration-300">
          {/* Laser Scanner Sweep Line over preview */}
          <div className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_12px_#10B981] animate-laser-sweep z-20 pointer-events-none" />

          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={previewUrl} alt="Preview" className="h-full object-contain drop-shadow-[0_4px_12px_rgba(0,0,0,0.6)]" />
          <button
            onClick={clearFile}
            className="absolute top-2 right-2 bg-slate-950/80 hover:bg-slate-900 text-slate-200 hover:text-white p-1.5 rounded-full border border-slate-700 transition-all z-30"
            title="Remove Image"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ) : (
        <div className="text-center transition-transform duration-200">
          <div className={`mx-auto h-12 w-12 rounded-full border border-slate-800 bg-slate-950 flex items-center justify-center mb-3 transition-colors ${dragOver ? "border-emerald-500 text-emerald-400" : "text-slate-500"}`}>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <span className="block text-sm font-semibold text-slate-200 mb-1">{label}</span>
          <span className="block text-xs font-mono text-slate-500">JPG, PNG, WEBP UP TO 10MB</span>
        </div>
      )}

      {error && <span className="text-xs text-red-500 mt-2">{error}</span>}
    </div>
  );
};
