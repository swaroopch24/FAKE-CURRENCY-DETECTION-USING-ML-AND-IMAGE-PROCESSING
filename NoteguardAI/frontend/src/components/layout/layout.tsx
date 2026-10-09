import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { AuthService } from "@/core/auth/auth-service";
import { AnimatedPage } from "@/components/motion/animated-page";

export const PageLayout = ({ children }: { children: React.ReactNode }) => {
  const navigate = useNavigate();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (!AuthService.isAuthenticated()) {
      navigate("/login");
    } else {
      setAuthorized(true);
    }
  }, [navigate]);

  if (!authorized) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-950 text-slate-100 font-sans">
        <div className="flex flex-col items-center gap-3">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
          <span className="text-sm text-slate-400">Verifying session security...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans antialiased">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Panel Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-slate-900/30">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <AnimatedPage>
            {children}
          </AnimatedPage>
        </main>
      </div>
    </div>
  );
};
