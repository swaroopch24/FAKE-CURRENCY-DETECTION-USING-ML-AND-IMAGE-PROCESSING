import React from "react";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { User, Cpu, Code2, ShieldCheck, Database, Layers } from "lucide-react";

export default function AboutPage() {
  const techStack = [
    { name: "Python", icon: <Code2 className="w-5 h-5 text-yellow-400" /> },
    { name: "TensorFlow", icon: <Cpu className="w-5 h-5 text-orange-400" /> },
    { name: "OpenCV", icon: <Layers className="w-5 h-5 text-blue-400" /> },
    { name: "Keras", icon: <Cpu className="w-5 h-5 text-red-400" /> },
    { name: "PostgreSQL", icon: <Database className="w-5 h-5 text-cyan-400" /> },
    { name: "FastAPI", icon: <ShieldCheck className="w-5 h-5 text-emerald-400" /> }
  ];

  const team = [
    { name: "Pothumarthi Sriram", role: "Developer" },
    { name: "Paravada Teja", role: "Developer" },
    { name: "Pamapana Veerendra", role: "Developer" },
    { name: "Chinthakayala Swaroop", role: "Developer" }
  ];

  return (
    <PageLayout>
      <div className="space-y-8 select-none max-w-5xl mx-auto pb-12">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-100 mb-2">About Project</h1>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            AI Based Fake Currency Detection System uses Deep Learning and Image Processing techniques to identify fake currency notes with high accuracy.
          </p>
        </div>

        {/* Technologies Used Section */}
        <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
          <h3 className="text-xs font-bold text-slate-300 mb-4 uppercase tracking-wider">Technologies Used</h3>
          <div className="flex flex-wrap gap-4">
            {techStack.map((tech) => (
              <div key={tech.name} className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-bold text-slate-200">
                {tech.icon}
                <span>{tech.name}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Team Members Section */}
        <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
          <h3 className="text-xs font-bold text-slate-300 mb-6 uppercase tracking-wider">Team Members</h3>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-6">
            {team.map((m) => (
              <div key={m.name} className="flex flex-col items-center text-center p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <div className="w-14 h-14 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-3">
                  <User className="w-6 h-6" />
                </div>
                <span className="text-xs font-bold text-slate-100">{m.name}</span>
                <span className="text-2xs text-slate-400">{m.role}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Guide Section */}
        <Card className="p-6 bg-slate-900/60 border-slate-800/80 backdrop-blur-md">
          <h3 className="text-xs font-bold text-slate-300 mb-4 uppercase tracking-wider">Project Guide</h3>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-xs">
              G
            </div>
            <div>
              <span className="block text-xs font-bold text-slate-100">Prof. Asim Makkad</span>
              <span className="text-2xs text-slate-400">Project Guide & Mentor</span>
            </div>
          </div>
        </Card>
      </div>
    </PageLayout>
  );
}
