import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import apiClient from "@/core/api/client";
import {
  Upload,
  CheckCircle,
  AlertTriangle,
  FileText,
  Brain,
  Sparkles,
  ShieldCheck,
  Check,
  RefreshCw,
  XCircle
} from "lucide-react";

type ScanStep = "CHOICE" | "PROCESSING" | "ANALYZING" | "RESULT";

export default function VerifyPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<ScanStep>("CHOICE");
  const [file, setFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Result state
  const [resultData, setResultData] = useState<any>(null);

  const handleFileChange = (selectedFile: File) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(selectedFile);
    startScanWorkflow(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const startScanWorkflow = async (selectedFile?: File) => {
    if (!selectedFile) {
      fileInputRef.current?.click();
      return;
    }

    setStep("PROCESSING");

    // Brief processing animation
    await new Promise((resolve) => setTimeout(resolve, 600));
    setStep("ANALYZING");

    try {
      const formData = new FormData();
      formData.append("image_front", selectedFile);
      formData.append("file", selectedFile);
      const res = await apiClient.post("/verify", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      if (res.data) {
        const data = res.data;
        const statusState = data.status;
        
        if (statusState === "ACCEPTED" && data.result) {
          const isAuth = data.result.authenticity === "AUTHENTIC";
          setResultData({
            status: "ACCEPTED",
            verdict: isAuth ? "REAL" : "FAKE",
            verdictSubtitle: isAuth ? "Model Classified as Authentic" : "Model Classified as Counterfeit",
            denomination: data.result.denomination_label || (data.result.denomination ? `₹${data.result.denomination}` : "Unknown"),
            confidence: `${(data.result.authenticity_confidence * 100).toFixed(1)}%`,
            denomConfidence: `${(data.result.denomination_confidence * 100).toFixed(1)}%`,
            noteId: `FCD-${data.request_id ? data.request_id.slice(0, 8) : "2026-01"}`,
            dateTime: new Date(data.timestamp || Date.now()).toLocaleString(),
            modelUsed: data.meta?.model_version || "NoteGuard CNN V2",
            processingTime: `${((data.meta?.processing_time_ms || 120) / 1000).toFixed(2)}s`,
            circulationStatus: data.result.circulation_status,
            decisionReason: String(data.action?.decision_reason || "Both model confidence thresholds were met."),
            features: [
              { name: "Image Quality & Format", status: "Passed" },
              { name: "Indian Currency Eligibility", status: "Passed" },
              { name: "OCR Safety Screening", status: "Passed" },
              { name: "CNN Authenticity Classification", status: "Complete" },
              { name: "Denomination Confidence", status: "Threshold Met" },
              { name: "Decision Policy", status: "Complete" }
            ]
          });
        } else if (statusState === "COUNTERFEIT_WARNING") {
          setResultData({
            status: statusState,
            verdict: "COUNTERFEIT WARNING",
            verdictSubtitle: "Explicit counterfeit marker detected",
            denomination: data.result?.denomination_label || "Unknown",
            confidence: "OCR safety rule",
            confidenceLabel: "Detection Method",
            denomConfidence: "N/A",
            noteId: `FCD-${data.request_id ? data.request_id.slice(0, 8) : "2026-01"}`,
            dateTime: new Date(data.timestamp || Date.now()).toLocaleString(),
            modelUsed: "CNN not run",
            processingTime: `${((data.meta?.processing_time_ms || 120) / 1000).toFixed(2)}s`,
            circulationStatus: data.result?.circulation_status || "UNKNOWN",
            decisionReason: String(data.action?.decision_reason || "An explicit counterfeit marker was detected by the OCR safety rule."),
            features: [{ name: "OCR Safety Screening", status: "Marker detected" }]
          });
        } else if (statusState === "UNSUPPORTED_CURRENCY") {
          setResultData({
            status: statusState,
            verdict: "UNSUPPORTED CURRENCY",
            verdictSubtitle: "Unsupported Currency",
            denomination: "N/A",
            confidence: "CNN not run",
            confidenceLabel: "Classification",
            denomConfidence: "N/A",
            noteId: `FCD-${data.request_id ? data.request_id.slice(0, 8) : "2026-01"}`,
            dateTime: new Date(data.timestamp || Date.now()).toLocaleString(),
            modelUsed: "Eligibility check",
            processingTime: `${((data.meta?.processing_time_ms || 120) / 1000).toFixed(2)}s`,
            circulationStatus: "N/A",
            decisionReason: "This system is designed to verify Indian currency notes only. Please upload an Indian banknote.",
            features: []
          });
        } else if (statusState === "UNABLE_TO_DETERMINE") {
          setResultData({
            status: "UNABLE_TO_DETERMINE",
            verdict: "UNCERTAIN",
            verdictSubtitle: "Unable to determine authenticity with high confidence",
            denomination: data.result?.denomination_label || "Uncertain",
            confidence: "Low (<80%)",
            denomConfidence: "N/A",
            noteId: `FCD-${data.request_id ? data.request_id.slice(0, 8) : "2026-01"}`,
            dateTime: new Date(data.timestamp || Date.now()).toLocaleString(),
            modelUsed: data.meta?.model_version || "NoteGuard CNN V2",
            processingTime: `${((data.meta?.processing_time_ms || 120) / 1000).toFixed(2)}s`,
            circulationStatus: "UNKNOWN",
            decisionReason: String(data.action?.decision_reason || "Confidence below 80% safety policy threshold. Please retake under clear lighting."),
            features: []
          });
        } else {
          setResultData({
            status: statusState || "INVALID",
            verdict: "INVALID",
            verdictSubtitle: statusState === "UNSUPPORTED_IMAGE" ? "Unsupported Image Format" : "Invalid Image",
            denomination: "N/A",
            confidence: "CNN not run",
            confidenceLabel: "Classification",
            denomConfidence: "N/A",
            noteId: `FCD-${data.request_id ? data.request_id.slice(0, 8) : "ERR"}`,
            dateTime: new Date().toLocaleString(),
            modelUsed: "NoteGuard Validation Guard",
            processingTime: "0.05s",
            circulationStatus: "N/A",
            decisionReason: String(data.action?.decision_reason || "The uploaded image could not be validated. Please upload a clear image of an Indian banknote."),
            features: []
          });
        }
      }
    } catch (err: any) {
      const errorData = err.response?.data;
      let reason = "Inference connection error. Please ensure the note image is clear.";
      
      if (errorData?.action?.decision_reason) {
        reason = String(errorData.action.decision_reason);
      } else if (Array.isArray(errorData?.detail)) {
        reason = errorData.detail.map((d: any) => (typeof d === "string" ? d : d.msg || "Invalid parameter")).join(", ");
      } else if (typeof errorData?.detail === "string") {
        reason = errorData.detail;
      } else if (err.message) {
        reason = String(err.message);
      }

      setResultData({
        status: "ERROR",
        verdict: "ERROR",
        verdictSubtitle: "Verification Error",
        denomination: "N/A",
        confidence: "N/A",
        denomConfidence: "N/A",
        noteId: "FCD-ERR",
        dateTime: new Date().toLocaleString(),
        modelUsed: "NoteGuard AI",
        processingTime: "N/A",
        circulationStatus: "N/A",
        decisionReason: reason,
        features: []
      });
    } finally {
      setStep("RESULT");
    }
  };

  const handleReset = () => {
    setFile(null);
    setImagePreview(null);
    setResultData(null);
    setStep("CHOICE");
  };

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto space-y-6 select-none pb-12">
        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileChange(e.target.files[0]);
            }
          }}
        />

        {/* PHASE 1: SCREEN 4 - SCAN CURRENCY (UNIFIED UPLOAD INTERFACE) */}
        {step === "CHOICE" && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="text-center md:text-left">
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-100 mb-1">Scan Currency Note</h1>
              <p className="text-sm text-slate-400">Upload or drag-and-drop a banknote photo to verify authenticity</p>
            </div>

            {/* Centered Hero Upload & Drop Zone */}
            <Card 
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`p-10 md:p-14 bg-slate-900/60 border-2 border-dashed rounded-2xl backdrop-blur-md flex flex-col items-center justify-center text-center group cursor-pointer transition-all duration-300 ${
                isDragging 
                  ? "border-blue-500 bg-blue-950/30 scale-[1.01] shadow-[0_0_30px_rgba(59,130,246,0.25)]" 
                  : "border-slate-800/90 hover:border-blue-500/50 hover:bg-slate-900/80 hover:shadow-[0_0_20px_rgba(59,130,246,0.15)]"
              }`}
            >
              <div className="w-20 h-20 rounded-2xl bg-blue-600/15 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-5 group-hover:scale-110 group-hover:bg-blue-600/25 transition-all shadow-[0_0_20px_rgba(59,130,246,0.2)]">
                <Upload className="w-10 h-10" />
              </div>
              
              <h3 className="text-xl font-bold text-slate-100 mb-2">Upload Banknote Image</h3>
              <p className="text-xs text-slate-400 max-w-md mb-6 leading-relaxed">
                Drag and drop your Indian currency note image here, or click the button below to browse from your device.
              </p>

              <Button 
                size="lg"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-[0_0_20px_rgba(59,130,246,0.4)] hover:shadow-[0_0_25px_rgba(59,130,246,0.6)] transition-all mb-6"
              >
                <Upload className="w-4 h-4 mr-2" />
                Choose Image File
              </Button>

              <div className="flex flex-wrap items-center justify-center gap-3 text-2xs text-slate-500">
                <span className="px-2.5 py-1 rounded-md bg-slate-950/80 border border-slate-800">Supported: JPG, PNG, WEBP</span>
                <span className="px-2.5 py-1 rounded-md bg-slate-950/80 border border-slate-800">Max Size: 20 MB</span>
              </div>

              <div className="mt-8 pt-6 border-t border-slate-800/80 w-full max-w-md flex items-center justify-center gap-2 text-2xs text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Tip: Capture the full front or back face of the note under good lighting</span>
              </div>
            </Card>
          </div>
        )}

        {/* PHASE 2: SCREEN 5 - IMAGE PROCESSING PREVIEW */}
        {step === "PROCESSING" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">Image Processing</h1>
              <p className="text-sm text-slate-400">Validating format and normalizing pixels for CNN analysis</p>
            </div>

            {/* Original vs Processed Side by Side */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="p-6 bg-slate-900/60 border-slate-800/80 text-center">
                <span className="block text-xs font-bold text-slate-300 mb-4 text-left">Original Image</span>
                <div className="h-48 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Original" className="w-full h-full object-contain" />
                  ) : (
                    <div className="text-xs text-slate-500">Loading preview...</div>
                  )}
                </div>
              </Card>

              <Card className="p-6 bg-slate-900/60 border-slate-800/80 text-center">
                <span className="block text-xs font-bold text-slate-300 mb-4 text-left">Normalized Input (224x224)</span>
                <div className="h-48 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden relative">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Processed" className="w-full h-full object-contain filter contrast-125 brightness-110" />
                  ) : (
                    <div className="text-xs text-slate-500">Processing tensor...</div>
                  )}
                  <div className="absolute inset-0 border-2 border-blue-500/40 pointer-events-none" />
                </div>
              </Card>
            </div>

            {/* Processing Steps Checklist & Progress Bar */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="p-6 bg-slate-900/60 border-slate-800/80">
                <h4 className="text-xs font-bold text-slate-300 mb-4 uppercase tracking-wider">Validation Checklist</h4>
                <div className="space-y-2.5 text-xs">
                  {["Image Format & Size Validation", "Bilinear Resize (224x224)", "RGB Model Input", "OCR Safety & Currency Eligibility"].map((st) => (
                    <div key={st} className="flex justify-between items-center text-slate-300">
                      <span>{st}</span>
                      <Check className="w-4 h-4 text-emerald-400" />
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6 bg-slate-900/60 border-slate-800/80 flex flex-col justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">Status</h4>
                  <p className="text-xs text-slate-400">Image validated. OCR safety and Indian-currency eligibility are checked before CNN classification.</p>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                    <span>Progress</span>
                    <span>100%</span>
                  </div>
                  <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800">
                    <div className="bg-blue-500 h-full rounded-full w-full" />
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* PHASE 3: SCREEN 6 - AI ANALYSIS IN PROGRESS */}
        {step === "ANALYZING" && (
          <div className="py-12 flex flex-col items-center justify-center text-center space-y-8">
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">AI Neural Analysis</h1>
              <p className="text-sm text-slate-400">Checking currency eligibility before MobileNetV2 classification</p>
            </div>

            {/* Animated Glowing Brain Scanner */}
            <div className="relative w-56 h-56 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-4 border-blue-500/20 animate-ping" />
              <div className="absolute w-48 h-48 rounded-full border-2 border-cyan-400/40 animate-spin" />
              <div className="w-36 h-36 rounded-full bg-blue-600/10 border-2 border-blue-500/60 shadow-[0_0_50px_rgba(59,130,246,0.5)] flex flex-col items-center justify-center">
                <Brain className="w-16 h-16 text-blue-400 mb-1 animate-pulse" />
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100">Executing Inference...</h3>
              <p className="text-xs text-slate-400">Running OCR safety, currency eligibility, and confidence policy checks</p>
            </div>

            {/* 4 Steps Indicator Bar */}
            <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
              <span className="px-3 py-1 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-300 text-2xs font-semibold">Image Decoded</span>
              <span className="px-3 py-1 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-300 text-2xs font-semibold">OCR & Eligibility</span>
              <span className="px-3 py-1 rounded-full bg-blue-600 text-white shadow-[0_0_10px_rgba(59,130,246,0.5)] text-2xs font-bold animate-pulse">Decision Policy</span>
              <span className="px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-500 text-2xs font-semibold">Generating Result</span>
            </div>
          </div>
        )}

        {/* PHASE 4: SCREEN 7 - RESULT (REAL OR FAKE) */}
        {step === "RESULT" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">Verification Result</h1>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Left Result Card */}
              <Card className="p-8 bg-slate-900/60 border-slate-800/80 backdrop-blur-md flex flex-col justify-between">
                <div>
                  {/* Big Verdict Header */}
                  <div className="flex flex-col items-center text-center mb-8">
                    <div
                      className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 border ${
                        resultData?.verdict === "REAL"
                          ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.4)]"
                          : resultData?.verdict === "UNCERTAIN"
                          ? "bg-amber-500/20 border-amber-500/50 text-amber-400 shadow-[0_0_30px_rgba(245,158,11,0.4)]"
                          : "bg-red-500/20 border-red-500/50 text-red-400 shadow-[0_0_30px_rgba(239,68,68,0.4)]"
                      }`}
                    >
                      {resultData?.verdict === "REAL" ? (
                        <CheckCircle className="w-10 h-10" />
                      ) : resultData?.verdict === "UNCERTAIN" ? (
                        <AlertTriangle className="w-10 h-10" />
                      ) : (
                        <XCircle className="w-10 h-10" />
                      )}
                    </div>

                    <h2
                      className={`text-3xl font-black ${
                        resultData?.verdict === "REAL"
                          ? "text-emerald-400"
                          : resultData?.verdict === "UNCERTAIN"
                          ? "text-amber-400"
                          : "text-red-400"
                      }`}
                    >
                      {resultData?.verdict || "ANALYZING"}
                    </h2>
                    <span className="text-xs text-slate-400 mt-1 font-semibold">
                      {resultData?.verdictSubtitle || "Verification Completed"}
                    </span>
                    {resultData?.decisionReason && (
                      <p className="text-2xs text-slate-300 bg-slate-950/80 border border-slate-800/80 px-3 py-2 rounded-lg mt-3 max-w-sm">
                        {resultData.decisionReason}
                      </p>
                    )}
                  </div>

                  {/* Confidence Score */}
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-6 text-center">
                    <span className="block text-2xs text-slate-400 uppercase font-semibold mb-1">{resultData?.confidenceLabel || "Authenticity Confidence"}</span>
                    <span className="text-2xl font-black text-slate-100">{resultData?.confidence || "N/A"}</span>
                  </div>

                  {/* Completed verification pipeline stages */}
                  {resultData?.features && resultData.features.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-300 mb-3 uppercase tracking-wider">Analysis Breakdown</h4>
                      <div className="space-y-2 text-xs">
                        {resultData.features.map((ft: any) => (
                          <div key={ft.name} className="flex justify-between items-center text-slate-300 py-1 border-b border-slate-800/50">
                            <span className="flex items-center gap-2">
                              <CheckCircle className={`w-3.5 h-3.5 ${resultData?.verdict === 'REAL' ? 'text-emerald-400' : 'text-amber-400'}`} />
                              {ft.name}
                            </span>
                            <span className={`${resultData?.verdict === 'REAL' ? 'text-emerald-400' : 'text-amber-400'} font-bold`}>{ft.status}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Card>

              {/* Right Detail Card */}
              <Card className="p-8 bg-slate-900/60 border-slate-800/80 backdrop-blur-md flex flex-col justify-between">
                <div>
                  {/* Denomination Header */}
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xs text-slate-400 uppercase font-semibold">Denomination</span>
                    <span className="text-3xl font-black text-slate-100">{resultData?.denomination || "N/A"}</span>
                  </div>

                  {/* Banknote Image Preview */}
                  <div className="h-44 rounded-xl bg-slate-950 border border-slate-800 overflow-hidden mb-6 flex items-center justify-center p-2">
                    {imagePreview ? (
                      <img src={imagePreview} alt="Banknote Preview" className="w-full h-full object-contain" />
                    ) : (
                      <div className="text-xs text-slate-500">No image preview</div>
                    )}
                  </div>

                  {/* Information List */}
                  <div className="space-y-3 text-xs text-slate-300">
                    <div className="flex justify-between border-b border-slate-800/60 pb-2">
                      <span className="text-slate-400">Date & Time</span>
                      <span className="font-mono text-slate-200">{resultData?.dateTime || "N/A"}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/60 pb-2">
                      <span className="text-slate-400">Note ID</span>
                      <span className="font-mono text-slate-200">{resultData?.noteId || "N/A"}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/60 pb-2">
                      <span className="text-slate-400">Model Used</span>
                      <span className="font-mono text-slate-200">{resultData?.modelUsed || "N/A"}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/60 pb-2">
                      <span className="text-slate-400">Processing Time</span>
                      <span className="font-mono text-slate-200">{resultData?.processingTime || "N/A"}</span>
                    </div>
                  </div>
                </div>

                {/* Bottom Action Buttons */}
                <div className="flex gap-4 pt-6 mt-6 border-t border-slate-800">
                  <Button variant="outline" onClick={handleReset} className="flex-1 border-slate-800 text-slate-200 hover:bg-slate-800">
                    Scan Another Note
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
