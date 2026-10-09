import React, { useEffect, useState } from "react";
import { Search, Bell, User } from "lucide-react";
import { AuthService } from "@/core/auth/auth-service";

export const Navbar = () => {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    setProfile(AuthService.getUserProfile());
  }, []);

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0B0F19]/60 px-6 flex items-center justify-between backdrop-blur-md select-none">
      {/* Search Input Bar */}
      <div className="relative w-72">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search..."
          className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-all"
        />
      </div>

      {/* Right User & Notification Controls */}
      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <button className="p-2 rounded-lg border border-slate-800/80 bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition-all relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500" />
        </button>

        {/* User Profile Badge */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="h-8 w-8 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-400 font-semibold text-xs">
            <User className="h-4 w-4" />
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-semibold text-slate-100 leading-tight">
              {profile?.full_name || "Admin Administrator"}
            </span>
            <span className="text-[10px] text-slate-400 capitalize">
              {profile?.role ? profile.role.toLowerCase().replace("role_", "") : "Administrator"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
