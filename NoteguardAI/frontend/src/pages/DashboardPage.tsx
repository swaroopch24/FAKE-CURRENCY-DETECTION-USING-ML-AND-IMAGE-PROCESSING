import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { AnimatedCounter } from "@/components/motion/animated-counter";
import { TrendingUp, CheckCircle, AlertTriangle, ShieldCheck, ArrowRight, RefreshCw, ScanLine } from "lucide-react";

import apiClient from "@/core/api/client";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalScans: 0,
    realNotes: 0,
    fakeNotes: 0,
    modelAccuracy: 95.49,
    realPercentage: 0,
    fakePercentage: 0
  });

  const fetchDashboardDetails = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.get("/dashboard/summary");
      const data = res.data;

      if (data.success && data.data) {
        const d = data.data;
        setStats({
          totalScans: d.total_scans,
          realNotes: d.real_notes,
          fakeNotes: d.fake_notes,
          modelAccuracy: d.model_accuracy || 95.49,
          realPercentage: d.real_percentage || (d.total_scans > 0 ? ((d.real_notes / d.total_scans) * 100) : 0),
          fakePercentage: d.fake_percentage || (d.total_scans > 0 ? ((d.fake_notes / d.total_scans) * 100) : 0)
        });
        setHistoryItems(d.recent_scans || []);
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardDetails();
  }, []);

  // Compute donut circumference (r=54 -> 2 * PI * 54 = 339.29)
  const totalCircumference = 339.29;
  const realOffset = stats.totalScans > 0 
    ? totalCircumference * (1 - stats.realPercentage / 100)
    : totalCircumference;
  const fakeOffset = stats.totalScans > 0 
    ? totalCircumference * (1 - stats.fakePercentage / 100)
    : totalCircumference;

  return (
    <PageLayout>
      <div className="space-y-6 select-none pb-12">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">System Dashboard</h1>
            <p className="text-sm text-slate-400">Live operational telemetry & CNN verification metrics</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDashboardDetails}
              className="text-xs border-slate-800 text-slate-300 hover:text-white"
            >
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Refresh Data
            </Button>
            <Button
              size="sm"
              onClick={() => navigate("/verify")}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-[0_0_15px_rgba(59,130,246,0.4)]"
            >
              <ScanLine className="h-3.5 w-3.5 mr-1.5" />
              Scan Currency
            </Button>
          </div>
        </div>

        {/* Top 4 KPI Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Total Scans Card */}
          <Card className="p-5 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-400">Total Scans (Live DB)</span>
            </div>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-slate-100">
                <AnimatedCounter value={stats.totalScans} />
              </span>
              <span className="text-2xs font-bold text-emerald-400 flex items-center gap-0.5">
                <TrendingUp className="h-3 w-3" /> Live
              </span>
            </div>
            <span className="text-[10px] text-slate-500">PostgreSQL Verified</span>
          </Card>

          {/* Real Notes Card */}
          <Card className="p-5 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-400">Genuine Notes</span>
            </div>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-emerald-400">
                <AnimatedCounter value={stats.realNotes} />
              </span>
              <span className="text-2xs font-bold text-emerald-400 flex items-center gap-0.5">
                {stats.realPercentage.toFixed(1)}%
              </span>
            </div>
            <span className="text-[10px] text-slate-500">Confirmed authentic</span>
          </Card>

          {/* Fake Notes Card */}
          <Card className="p-5 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-400">Counterfeit Notes</span>
            </div>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-red-400">
                <AnimatedCounter value={stats.fakeNotes} />
              </span>
              <span className="text-2xs font-bold text-red-400 flex items-center gap-0.5">
                {stats.fakePercentage.toFixed(1)}%
              </span>
            </div>
            <span className="text-[10px] text-slate-500">Intercepted fakes</span>
          </Card>

          {/* Model Accuracy Card */}
          <Card className="p-5 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-400">Model Test Accuracy</span>
            </div>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-slate-100">
                {stats.modelAccuracy}%
              </span>
              <span className="text-2xs font-bold text-emerald-400 flex items-center gap-0.5">
                <ShieldCheck className="h-3 w-3" /> MobileNetV2
              </span>
            </div>
            <span className="text-[10px] text-slate-500">Evaluated on 488 unseen notes</span>
          </Card>
        </div>

        {/* Dashboard Main Grid: Left Table (2/3) + Right Analytics Charts (1/3) */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Recent Scans Table (Left 2 cols) */}
          <Card className="lg:col-span-2 p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-extrabold text-slate-100">Recent Verification Scans</h3>
                <p className="text-2xs text-slate-400">Real transaction audit trail from the database</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/history")}
                className="text-xs border-slate-800 text-blue-400 hover:text-blue-300"
              >
                View Full History
              </Button>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <span className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
              </div>
            ) : historyItems.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
                <ShieldCheck className="h-10 w-10 text-slate-600" />
                <h4 className="text-sm font-bold text-slate-300">No verification scans recorded yet</h4>
                <p className="text-xs text-slate-500 max-w-sm">
                  Click the button below to upload a banknote image and run your first neural scan.
                </p>
                <Button 
                  size="sm"
                  onClick={() => navigate("/verify")}
                  className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs mt-2"
                >
                  Scan Banknote Now
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="border-slate-800">
                    <TableHead className="text-xs text-slate-400 font-semibold">Scan ID</TableHead>
                    <TableHead className="text-xs text-slate-400 font-semibold">Verdict</TableHead>
                    <TableHead className="text-xs text-slate-400 font-semibold">Denomination</TableHead>
                    <TableHead className="text-xs text-slate-400 font-semibold">Confidence</TableHead>
                    <TableHead className="text-xs text-slate-400 font-semibold">Date & Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historyItems.map((item, idx) => {
                    const isReal = item.result === "REAL" || item.authenticity === "AUTHENTIC" || item.system_verdict === "AUTHENTIC";
                    const isFake = item.result === "FAKE" || item.authenticity === "COUNTERFEIT" || item.system_verdict === "COUNTERFEIT";
                    const denom = item.denomination ? (String(item.denomination).startsWith("₹") ? item.denomination : `₹${item.denomination}`) : "₹500";
                    const conf = item.confidence || `${(item.confidence_score * 100).toFixed(1)}%`;
                    const dt = item.datetime || (item.created_at ? new Date(item.created_at).toLocaleString() : "Just now");
                    const shortId = item.id ? item.id.slice(0, 8) : `SCAN-${idx + 1}`;

                    return (
                      <TableRow 
                        key={item.id || idx} 
                        className="border-slate-800/60 hover:bg-slate-800/40 cursor-pointer" 
                        onClick={() => navigate("/verify")}
                      >
                        <TableCell className="font-mono text-2xs text-slate-400">
                          {shortId}
                        </TableCell>
                        <TableCell>
                          <span
                            className={`px-3 py-1 rounded-md text-2xs font-extrabold tracking-wider uppercase border ${
                              isReal
                                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                                : isFake
                                ? "bg-red-500/20 text-red-400 border-red-500/40 shadow-[0_0_10px_rgba(239,68,68,0.2)]"
                                : "bg-amber-500/20 text-amber-400 border-amber-500/40"
                            }`}
                          >
                            {isReal ? "REAL" : isFake ? "FAKE" : "UNCERTAIN"}
                          </span>
                        </TableCell>
                        <TableCell className="font-bold text-slate-200 text-xs">{denom}</TableCell>
                        <TableCell className="font-mono text-slate-300 text-xs">{conf}</TableCell>
                        <TableCell className="text-2xs text-slate-400">{dt}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}
          </Card>

          {/* Right Panel: Charts (1 col) */}
          <div className="space-y-6">
            {/* Real vs Fake Donut Chart Card */}
            <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
              <h3 className="text-sm font-extrabold text-slate-100 mb-4">Real vs Fake Ratio</h3>

              <div className="flex items-center justify-center py-2 relative">
                {/* SVG Donut Ring */}
                <svg className="w-36 h-36 transform -rotate-90">
                  <circle cx="72" cy="72" r="54" stroke="#1E293B" strokeWidth="16" fill="transparent" />
                  {/* Real Notes Green Arc */}
                  {stats.totalScans > 0 && stats.realPercentage > 0 && (
                    <circle
                      cx="72"
                      cy="72"
                      r="54"
                      stroke="#10B981"
                      strokeWidth="16"
                      strokeDasharray={totalCircumference}
                      strokeDashoffset={realOffset}
                      strokeLinecap="round"
                      fill="transparent"
                    />
                  )}
                  {/* Fake Notes Red Arc */}
                  {stats.totalScans > 0 && stats.fakePercentage > 0 && (
                    <circle
                      cx="72"
                      cy="72"
                      r="54"
                      stroke="#EF4444"
                      strokeWidth="16"
                      strokeDasharray={totalCircumference}
                      strokeDashoffset={fakeOffset}
                      strokeLinecap="round"
                      fill="transparent"
                      className="transform rotate-[180deg] origin-center"
                    />
                  )}
                </svg>

                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-xl font-black text-slate-100">{stats.totalScans}</span>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">Total Scans</span>
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 mt-4 text-xs font-semibold">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-slate-300">Real ({stats.realPercentage.toFixed(1)}%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-slate-300">Fake ({stats.fakePercentage.toFixed(1)}%)</span>
                </div>
              </div>
            </Card>

            {/* Neural Architecture Card */}
            <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md space-y-3">
              <div className="flex items-center gap-2 text-slate-200 text-xs font-bold">
                <ShieldCheck className="h-4 w-4 text-blue-400" />
                <span>Production AI Status</span>
              </div>
              <div className="space-y-2 text-xs text-slate-400">
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span>Architecture</span>
                  <span className="font-mono text-slate-200">MobileNetV2 Transfer</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span>Authenticity Accuracy</span>
                  <span className="font-mono text-emerald-400 font-bold">95.49%</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span>Denomination Accuracy</span>
                  <span className="font-mono text-slate-200">82.17%</span>
                </div>
                <div className="flex justify-between">
                  <span>Confidence Safety Policy</span>
                  <span className="font-mono text-slate-200">&ge; 80.0% Cutoff</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
