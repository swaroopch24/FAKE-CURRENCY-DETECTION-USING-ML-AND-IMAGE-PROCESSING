import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/core/utils/cn";
import { AuthService } from "@/core/auth/auth-service";
import {
  LayoutDashboard,
  Scan,
  History,
  BarChart3,
  Users,
  Settings,
  Info,
  LogOut,
  Shield
} from "lucide-react";

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

export const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const pathname = location.pathname;
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    setProfile(AuthService.getUserProfile());
  }, []);

  const navItems: SidebarItem[] = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: <LayoutDashboard className="h-5 w-5" />
    },
    {
      name: "Scan Currency",
      href: "/verify",
      icon: <Scan className="h-5 w-5" />
    },
    {
      name: "History",
      href: "/history",
      icon: <History className="h-5 w-5" />
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: <BarChart3 className="h-5 w-5" />
    },
    {
      name: "Users",
      href: "/admin",
      icon: <Users className="h-5 w-5" />
    },
    {
      name: "Settings",
      href: "/settings",
      icon: <Settings className="h-5 w-5" />
    },
    {
      name: "About",
      href: "/about",
      icon: <Info className="h-5 w-5" />
    }
  ];

  const handleLogoutClick = () => {
    AuthService.logout();
    navigate("/logout");
  };

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#0B0F19] p-5 text-slate-200 flex flex-col justify-between select-none">
      <div>
        {/* Brand Header */}
        <Link to="/" className="group flex items-center gap-3 mb-8 px-2 cursor-pointer">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30 group-hover:scale-105 transition-all duration-300">
            <Shield className="h-5 w-5 fill-current text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold tracking-wider text-slate-100 text-lg leading-tight group-hover:text-blue-400 transition-colors">
              FCD SYSTEM
            </span>
            <span className="text-[10px] tracking-widest uppercase text-blue-400 font-semibold">
              Fake Currency Detection
            </span>
          </div>
        </Link>

        {/* Navigation list */}
        <nav className="space-y-1.5">
          {navItems.map(item => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  "group flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ease-out",
                  isActive
                    ? "bg-blue-600 text-white shadow-[0_0_15px_rgba(59,130,246,0.4)] font-semibold"
                    : "hover:bg-slate-900/80 hover:text-slate-100 text-slate-400 hover:translate-x-1"
                )}
              >
                <span className={cn(
                  "transition-all duration-200",
                  isActive ? "text-white" : "group-hover:text-blue-400"
                )}>
                  {item.icon}
                </span>
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Logout & Account Section */}
      <div className="border-t border-slate-800/80 pt-4 px-2 space-y-3">
        <button
          onClick={handleLogoutClick}
          className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
        >
          <LogOut className="h-5 w-5 text-slate-400 group-hover:text-red-400" />
          <span>Logout</span>
        </button>

        <div className="flex items-center gap-3 pt-2 border-t border-slate-900">
          <div className="h-8 w-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center font-bold text-blue-400 text-xs">
            {profile?.full_name ? profile.full_name.charAt(0).toUpperCase() : "A"}
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="text-xs font-semibold text-slate-200 truncate max-w-[120px]">
              {profile?.full_name || "Admin Administrator"}
            </span>
            <span className="text-[10px] text-slate-500 truncate capitalize">
              {profile?.role ? profile.role.toLowerCase().replace("role_", "") : "Administrator"}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
