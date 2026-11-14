"use client";

import React from "react";
import { Compass, Activity, Server, FileText, TrendingUp, BarChart3, Globe2 } from "lucide-react";
import { HealthStatus } from "@/lib/api";

export type ActiveTab = "overview" | "trends" | "forecast" | "geographic" | "reports";

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  health: HealthStatus | null;
  loading: boolean;
  onRefreshHealth: () => void;
}

export function Navbar({
  activeTab,
  setActiveTab,
  health,
  loading,
  onRefreshHealth,
}: NavbarProps) {
  const isHealthy = health?.status === "healthy";

  const navItems: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <Compass className="w-4 h-4" /> },
    { id: "trends", label: "Trend Explorer", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "forecast", label: "Forecast Explorer", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "geographic", label: "Geographic Context", icon: <Globe2 className="w-4 h-4" /> },
    { id: "reports", label: "Reports & Data", icon: <FileText className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 sm:px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      {/* Brand & Mission Tag */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-cyan-500 p-0.5 shadow-lg shadow-emerald-950/50">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center text-emerald-400">
            <Compass className="w-5 h-5 animate-spin-slow" />
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
              EarthScope
            </h1>
            <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-700/60 text-emerald-300">
              Stage 7 Live
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">
            NASA Space Apps Challenge 2026: Be an Earth System Trend Detective!
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex items-center gap-1 overflow-x-auto py-1 sm:py-0 border-t md:border-t-0 border-slate-800/60">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                isActive
                  ? "bg-slate-800 text-white shadow-sm border border-slate-700 text-emerald-400"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              }`}
            >
              <span className={isActive ? "text-emerald-400" : "text-slate-400"}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Backend Health Pill */}
      <div className="hidden lg:flex items-center gap-3">
        <button
          onClick={onRefreshHealth}
          title="Click to check backend health status"
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 hover:border-slate-700 transition text-xs text-slate-300"
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isHealthy
                ? "bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400"
                : "bg-amber-400 shadow-sm shadow-amber-400"
            }`}
          />
          <Server className="w-3.5 h-3.5 text-slate-400" />
          <span>
            {loading
              ? "Checking..."
              : isHealthy
              ? `API Connected (v${health.version})`
              : "API Standby"}
          </span>
        </button>
      </div>
    </header>
  );
}
