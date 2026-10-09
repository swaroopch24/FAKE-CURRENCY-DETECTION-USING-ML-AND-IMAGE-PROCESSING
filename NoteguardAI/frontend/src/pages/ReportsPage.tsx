import React, { useState } from "react";
import { PageLayout } from "@/components/layout/layout";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ReportsPage() {
  const [reports] = useState<any[]>([]);

  const handleDownload = (id: string) => {
    alert(`Downloading report file context for: ${id}`);
  };

  const handlePrint = (id: string) => {
    alert(`Preparing print layout frame for report: ${id}`);
  };

  return (
    <PageLayout>
      <div className="space-y-8 select-none">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Verification Reports</h1>
          <p className="text-sm text-slate-500">Download and print professional PDF verification audits.</p>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Report ID</TableHead>
              <TableHead>Linked Scan</TableHead>
              <TableHead>Denomination</TableHead>
              <TableHead>Verdict Decision</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Compiled Date</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.map(rep => (
              <TableRow key={rep.id}>
                <TableCell className="font-semibold text-slate-300">{rep.id}</TableCell>
                <TableCell className="font-mono text-xs text-slate-400">#{rep.scan_id}</TableCell>
                <TableCell>{rep.denomination} INR</TableCell>
                <TableCell>
                  <Badge variant={rep.verdict === "authentic" ? "success" : "error"}>
                    {rep.verdict}
                  </Badge>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-slate-400 font-medium">{rep.status}</span>
                </TableCell>
                <TableCell className="text-xs text-slate-500">{new Date(rep.date).toLocaleString()}</TableCell>
                <TableCell className="text-right space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handlePrint(rep.id)}>
                    Print
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleDownload(rep.id)}>
                    Download
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </PageLayout>
  );
}
