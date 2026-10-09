import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircle, Shield } from "lucide-react";

export default function LogoutPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#070B14] flex flex-col items-center justify-center p-6 relative overflow-hidden select-none">
      {/* Brand Header */}
      <div className="flex items-center gap-3 mb-8 cursor-pointer" onClick={() => navigate("/")}>
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
          <Shield className="h-6 w-6 fill-current text-white" />
        </div>
        <span className="font-black tracking-wider text-slate-100 text-xl">FCD SYSTEM</span>
      </div>

      {/* Main Logout Confirmation Card */}
      <Card className="w-full max-w-md p-10 bg-slate-900/60 border-slate-800/80 backdrop-blur-xl flex flex-col items-center text-center shadow-[0_0_50px_rgba(0,0,0,0.8)]">
        <div className="w-20 h-20 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(16,185,129,0.4)]">
          <CheckCircle className="w-10 h-10" />
        </div>

        <h2 className="text-2xl font-black text-slate-100 mb-2">Logged Out Successfully!</h2>
        <p className="text-xs text-slate-400 mb-8">Thank you for using our system.</p>

        <Button
          onClick={() => navigate("/login")}
          className="px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-[0_0_20px_rgba(59,130,246,0.4)] transition-all"
        >
          Back to Login
        </Button>
      </Card>

      <footer className="absolute bottom-6 text-center text-2xs text-slate-500">
        &copy; {new Date().getFullYear()} FCD System | All Rights Reserved
      </footer>
    </div>
  );
}
