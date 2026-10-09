import React from "react";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Users, Database, Cpu, FileText, Settings, ShieldAlert } from "lucide-react";

export default function AdminPage() {
  const adminCards = [
    {
      title: "Manage Users",
      desc: "Add, Edit, Remove Users",
      icon: <Users className="w-8 h-8 text-blue-400" />,
      color: "border-blue-500/30 bg-blue-500/10"
    },
    {
      title: "Dataset Management",
      desc: "Upload and manage dataset",
      icon: <Database className="w-8 h-8 text-cyan-400" />,
      color: "border-cyan-500/30 bg-cyan-500/10"
    },
    {
      title: "Train Model",
      desc: "Train AI model with new data",
      icon: <Cpu className="w-8 h-8 text-purple-400" />,
      color: "border-purple-500/30 bg-purple-500/10"
    },
    {
      title: "System Logs",
      desc: "View system activity logs",
      icon: <FileText className="w-8 h-8 text-amber-400" />,
      color: "border-amber-500/30 bg-amber-500/10"
    },
    {
      title: "Settings",
      desc: "Configure system settings",
      icon: <Settings className="w-8 h-8 text-emerald-400" />,
      color: "border-emerald-500/30 bg-emerald-500/10"
    },
    {
      title: "Backup & Restore",
      desc: "Backup or restore database",
      icon: <ShieldAlert className="w-8 h-8 text-indigo-400" />,
      color: "border-indigo-500/30 bg-indigo-500/10"
    }
  ];

  return (
    <PageLayout>
      <div className="space-y-6 select-none max-w-5xl mx-auto pb-12">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">Admin Panel</h1>
          <p className="text-sm text-slate-400">Manage system settings and data</p>
        </div>

        {/* 6 Action Grid Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          {adminCards.map((c) => (
            <Card
              key={c.title}
              className="p-8 bg-slate-900/60 border-slate-800/80 backdrop-blur-md flex flex-col items-center justify-center text-center group hover:border-blue-500/50 hover:scale-[1.02] transition-all cursor-pointer"
            >
              <div className={`w-16 h-16 rounded-2xl ${c.color} border flex items-center justify-center mb-4 group-hover:scale-110 transition-all`}>
                {c.icon}
              </div>
              <h3 className="text-base font-bold text-slate-100 mb-1">{c.title}</h3>
              <p className="text-xs text-slate-400">{c.desc}</p>
            </Card>
          ))}
        </div>
      </div>
    </PageLayout>
  );
}
