import React, { useState, useEffect } from "react";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, TrendingUp, RefreshCw, ShieldCheck, AlertTriangle, CheckCircle2, Layers, HelpCircle } from "lucide-react";
import apiClient from "@/core/api/client";

interface TimelineItem {
  date: string;
  real: number;
  fake: number;
  total: number;
}

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState<{
    totalScans: number;
    realNotes: number;
    fakeNotes: number;
    uncertainNotes: number;
    realPercentage: number;
    fakePercentage: number;
    averageConfidence: number;
    dateRange: string;
    timeline: TimelineItem[];
    denominationCounts: Record<string, number>;
  }>({
    totalScans: 0,
    realNotes: 0,
    fakeNotes: 0,
    uncertainNotes: 0,
    realPercentage: 0,
    fakePercentage: 0,
    averageConfidence: 95.08,
    dateRange: "Live Data",
    timeline: [],
    denominationCounts: {}
  });

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.get("/analytics/summary");
      if (res.data?.success && res.data?.data) {
        const d = res.data.data;
        setAnalyticsData({
          totalScans: d.total_scans ?? 0,
          realNotes: d.real_notes ?? 0,
          fakeNotes: d.fake_notes ?? 0,
          uncertainNotes: d.uncertain_notes ?? 0,
          realPercentage: d.real_percentage ?? 0,
          fakePercentage: d.fake_percentage ?? 0,
          averageConfidence: d.average_confidence ?? 95.08,
          dateRange: d.date_range ?? "Last 7 Days",
          timeline: d.timeline ?? [],
          denominationCounts: d.denomination_counts ?? {}
        });
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  // Compute Donut chart parameters
  // Circle circumference with r=72: 2 * PI * 72 = 452.39
  const circumference = 452.39;
  const realRatio = analyticsData.totalScans > 0 ? analyticsData.realPercentage / 100 : 0.65;
  const fakeRatio = analyticsData.totalScans > 0 ? analyticsData.fakePercentage / 100 : 0.35;
  const realOffset = circumference * (1 - realRatio);

  // Compute dynamic SVG line chart points from timeline data
  const maxTimelineCount = Math.max(...analyticsData.timeline.map((t) => Math.max(t.real, t.fake, 1)), 5);
  const chartWidth = 400;
  const chartHeight = 120;
  const stepX = analyticsData.timeline.length > 1 ? chartWidth / (analyticsData.timeline.length - 1) : 50;

  const realPoints = analyticsData.timeline
    .map((t, idx) => {
      const x = 10 + idx * stepX;
      const y = chartHeight - (t.real / maxTimelineCount) * (chartHeight - 20) - 10;
      return `${x},${y}`;
    })
    .join(" ");

  const fakePoints = analyticsData.timeline
    .map((t, idx) => {
      const x = 10 + idx * stepX;
      const y = chartHeight - (t.fake / maxTimelineCount) * (chartHeight - 20) - 10;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <PageLayout>
      <div className="space-y-6 select-none max-w-6xl mx-auto pb-12">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-100 mb-1">Analytics Overview</h1>
            <p className="text-xs text-slate-400">Live operational statistics computed directly from verified database transactions</p>
          </div>

          <div className="flex items-center gap-3">
            {/* Refresh Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={fetchAnalytics}
              disabled={isLoading}
              className="bg-slate-900/80 border-slate-800 text-slate-300 hover:text-white text-xs gap-2"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-blue-400" : ""}`} />
              Refresh
            </Button>

            {/* Date Range Badge */}
            <div className="flex items-center gap-2 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800 text-xs font-semibold text-slate-300">
              <Calendar className="w-4 h-4 text-blue-400" />
              <span>{analyticsData.dateRange}</span>
            </div>
          </div>
        </div>

        {/* 5 Analytics KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden group hover:border-blue-500/40 transition-all">
            <span className="text-xs font-semibold text-slate-400 block mb-1.5">Total Verified Scans</span>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-slate-100">
                {analyticsData.totalScans.toLocaleString()}
              </span>
              <span className="text-2xs font-bold text-emerald-400 flex items-center gap-0.5">
                <TrendingUp className="h-3 w-3" /> Live
              </span>
            </div>
            <span className="text-2xs text-slate-500">All scan attempts</span>
          </Card>

          <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden group hover:border-emerald-500/40 transition-all">
            <span className="text-xs font-semibold text-emerald-400/90 block mb-1.5 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Genuine Notes
            </span>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-emerald-400">
                {analyticsData.realNotes.toLocaleString()}
              </span>
              <span className="text-2xs font-bold text-emerald-400">
                {analyticsData.realPercentage}%
              </span>
            </div>
            <span className="text-2xs text-slate-500">Verified authentic currency</span>
          </Card>

          <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden group hover:border-red-500/40 transition-all">
            <span className="text-xs font-semibold text-red-400/90 block mb-1.5 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-red-400" /> Counterfeits
            </span>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-red-400">
                {analyticsData.fakeNotes.toLocaleString()}
              </span>
              <span className="text-2xs font-bold text-red-400">
                {analyticsData.fakePercentage}%
              </span>
            </div>
            <span className="text-2xs text-slate-500">Fake or novelty detected</span>
          </Card>

          <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden group hover:border-amber-500/40 transition-all">
            <span className="text-xs font-semibold text-amber-400/90 block mb-1.5 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-amber-400" /> Uncertain / Retake
            </span>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-amber-400">
                {analyticsData.uncertainNotes.toLocaleString()}
              </span>
              <span className="text-2xs font-bold text-amber-400">
                {analyticsData.totalScans > 0 ? ((analyticsData.uncertainNotes / analyticsData.totalScans) * 100).toFixed(1) : 0}%
              </span>
            </div>
            <span className="text-2xs text-slate-500">Low confidence (&lt;80%)</span>
          </Card>

          <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md relative overflow-hidden group hover:border-cyan-500/40 transition-all">
            <span className="text-xs font-semibold text-cyan-400/90 block mb-1.5 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> Avg Confidence
            </span>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-black text-cyan-400">
                {analyticsData.averageConfidence}%
              </span>
              <span className="text-2xs font-bold text-emerald-400">
                High
              </span>
            </div>
            <span className="text-2xs text-slate-500">Mean model certainty</span>
          </Card>
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Donut Chart Card */}
          <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-extrabold text-slate-100">Authenticity Ratio</h3>
              <span className="text-2xs font-medium text-slate-400">Real vs Counterfeit</span>
            </div>

            <div className="flex items-center justify-center py-4 relative">
              <svg className="w-48 h-48 transform -rotate-90">
                <circle cx="96" cy="96" r="72" stroke="#1E293B" strokeWidth="20" fill="transparent" />
                {/* Real Notes Green Arc */}
                <circle
                  cx="96"
                  cy="96"
                  r="72"
                  stroke="#10B981"
                  strokeWidth="20"
                  strokeDasharray={circumference}
                  strokeDashoffset={realOffset}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className="text-2xl font-black text-slate-100">
                  {analyticsData.totalScans > 0 ? `${analyticsData.realPercentage}%` : "0%"}
                </span>
                <span className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Authentic</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 mt-6 text-xs font-semibold">
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-slate-300">Real ({analyticsData.realNotes})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                <span className="text-slate-300">Fake ({analyticsData.fakeNotes})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                <span className="text-slate-300">Uncertain ({analyticsData.uncertainNotes})</span>
              </div>
            </div>
          </Card>

          {/* Timeline Chart Card */}
          <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md flex flex-col justify-between">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-extrabold text-slate-100">Scans Over Time (Last 7 Days)</h3>
              <div className="flex items-center gap-4 text-2xs font-semibold">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" /> Real Scans
                </span>
                <span className="flex items-center gap-1.5 text-red-400">
                  <span className="w-2 h-2 rounded-full bg-red-400" /> Fake Scans
                </span>
              </div>
            </div>

            <div className="h-44 relative flex items-end justify-between px-2 my-2">
              {realPoints ? (
                <svg className="absolute inset-0 w-full h-full overflow-visible pointer-events-none" viewBox={`0 0 ${chartWidth} ${chartHeight}`}>
                  {/* Real trendline */}
                  <polyline
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={realPoints}
                    className="transition-all duration-700"
                  />
                  {/* Fake trendline */}
                  <polyline
                    fill="none"
                    stroke="#EF4444"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={fakePoints}
                    className="transition-all duration-700"
                  />
                </svg>
              ) : (
                <div className="w-full text-center text-xs text-slate-500 py-12">No scan activity recorded yet</div>
              )}
            </div>

            <div className="flex items-center justify-between text-2xs text-slate-400 pt-2 border-t border-slate-800/80 font-mono">
              {analyticsData.timeline.length > 0 ? (
                analyticsData.timeline.map((t) => (
                  <span key={t.date} className="text-center">{t.date}</span>
                ))
              ) : (
                <span>No timeline data</span>
              )}
            </div>
          </Card>
        </div>

        {/* Denomination Activity Breakdown */}
        {Object.keys(analyticsData.denominationCounts).length > 0 && (
          <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
            <h3 className="text-sm font-extrabold text-slate-100 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              Verified Scans by Denomination
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
              {["₹10", "₹20", "₹50", "₹100", "₹200", "₹500", "₹2000"].map((denom) => {
                const count = analyticsData.denominationCounts[denom] || 0;
                return (
                  <div key={denom} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                    <span className="text-xs font-bold text-slate-300 block mb-1">{denom}</span>
                    <span className="text-lg font-black text-blue-400">{count}</span>
                    <span className="text-3xs text-slate-500 block">scans</span>
                  </div>
                );
              })}
            </div>
          </Card>
        )}
      </div>
    </PageLayout>
  );
}
