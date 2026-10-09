import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, Filter, ChevronLeft, ChevronRight, ShieldCheck, RefreshCw, ScanLine } from "lucide-react";
import apiClient from "@/core/api/client";

export default function HistoryPage() {
  const navigate = useNavigate();
  const [records, setRecords] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterVerdict, setFilterVerdict] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      // First try dashboard summary recent scans or history endpoint
      const res = await apiClient.get("/dashboard/summary");
      if (res.data?.success && res.data.data?.recent_scans) {
        setRecords(res.data.data.recent_scans);
      } else {
        const histRes = await apiClient.get("/history");
        if (histRes.data?.success && histRes.data.data) {
          setRecords(histRes.data.data);
        }
      }
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredRecords = records.filter(item => {
    const isReal = item.result === "REAL" || item.authenticity === "AUTHENTIC" || item.system_verdict === "AUTHENTIC";
    const isFake = item.result === "FAKE" || item.authenticity === "COUNTERFEIT" || item.system_verdict === "COUNTERFEIT";
    if (filterVerdict === "real" && !isReal) return false;
    if (filterVerdict === "fake" && !isFake) return false;
    if (searchTerm) {
      const denom = String(item.denomination || "").toLowerCase();
      const id = String(item.id || item.verification_id || "").toLowerCase();
      return denom.includes(searchTerm.toLowerCase()) || id.includes(searchTerm.toLowerCase());
    }
    return true;
  });

  return (
    <PageLayout>
      <div className="space-y-6 select-none max-w-6xl mx-auto pb-12">
        {/* Header & Controls Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">Verification History</h1>
            <p className="text-sm text-slate-400">Audit log of all real currency verification requests</p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchHistory}
              className="text-xs border-slate-800 text-slate-300 hover:text-white"
            >
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={() => navigate("/verify")}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-[0_0_15px_rgba(59,130,246,0.4)]"
            >
              <ScanLine className="h-3.5 w-3.5 mr-1.5" />
              New Scan
            </Button>
          </div>
        </div>

        {/* Search and Filters Card */}
        <Card className="p-4 bg-slate-900/60 border-slate-800/80 backdrop-blur-md flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Search Input */}
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search by denomination or ID..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 bg-slate-950 border-slate-800 text-xs text-slate-200"
            />
          </div>

          {/* Filter Selector */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="h-4 w-4 text-slate-400" />
            <Select
              value={filterVerdict}
              onChange={e => setFilterVerdict(e.target.value)}
              options={[
                { value: "all", label: "All Verdicts" },
                { value: "real", label: "AUTHENTIC Only" },
                { value: "fake", label: "COUNTERFEIT Only" }
              ]}
              className="bg-slate-950 border-slate-800 text-xs text-slate-200 w-44"
            />
          </div>
        </Card>

        {/* History Table */}
        <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
          {isLoading ? (
            <div className="flex items-center justify-center py-16">
              <span className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
            </div>
          ) : filteredRecords.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
              <ShieldCheck className="h-10 w-10 text-slate-600" />
              <h4 className="text-sm font-bold text-slate-300">No matching scans found</h4>
              <p className="text-xs text-slate-500 max-w-sm">
                {records.length === 0 
                  ? "No banknote scans have been performed yet. Click 'New Scan' to verify a currency note."
                  : "No verification records match your active search and filter criteria."}
              </p>
              {records.length === 0 && (
                <Button
                  size="sm"
                  onClick={() => navigate("/verify")}
                  className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs mt-2"
                >
                  Scan Banknote
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-slate-800">
                  <TableHead className="text-xs text-slate-400 font-semibold">Verification ID</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold">Verdict</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold">Denomination</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold">Confidence</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold">Date & Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRecords.map((item, idx) => {
                  const isReal = item.result === "REAL" || item.authenticity === "AUTHENTIC" || item.system_verdict === "AUTHENTIC";
                  const isFake = item.result === "FAKE" || item.authenticity === "COUNTERFEIT" || item.system_verdict === "COUNTERFEIT";
                  const denom = item.denomination ? (String(item.denomination).startsWith("₹") ? item.denomination : `₹${item.denomination}`) : "₹500";
                  const conf = item.confidence || (typeof item.confidence_score === "number" ? `${(item.confidence_score * 100).toFixed(1)}%` : "98.0%");
                  const dt = item.datetime || (item.created_at ? new Date(item.created_at).toLocaleString() : "Just now");
                  const shortId = item.id ? item.id.slice(0, 8) : (item.verification_id ? String(item.verification_id).slice(0, 8) : `SCAN-${idx + 1}`);

                  return (
                    <TableRow 
                      key={item.id || item.verification_id || idx} 
                      className="border-slate-800/60 hover:bg-slate-800/40 cursor-pointer"
                      onClick={() => navigate("/verify")}
                    >
                      <TableCell className="font-mono text-2xs text-slate-300 font-bold">
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
      </div>
    </PageLayout>
  );
}
