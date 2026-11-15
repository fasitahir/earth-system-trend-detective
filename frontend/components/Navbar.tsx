"use client";

import React from "react";
import { Compass, Server, FileText, TrendingUp, BarChart3, Globe2, ArrowUpRight } from "lucide-react";
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
    { id: "overview", label: "Home", icon: <Compass className="w-4 h-4" /> },
    { id: "trends", label: "What changed", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "forecast", label: "What comes next", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "geographic", label: "Where", icon: <Globe2 className="w-4 h-4" /> },
    { id: "reports", label: "Sources", icon: <FileText className="w-4 h-4" /> },
  ];

  return (
    <header className="earth-header sticky top-0 z-50 border-b px-4 sm:px-8 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      {/* Brand & Mission Tag */}
      <div className="flex items-center gap-3">
        <div className="earth-brand-mark">
          <span className="earth-brand-image" aria-hidden="true" />
          <span className="earth-brand-ring" aria-hidden="true" />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
              EarthScope
            </h1>
            <span className="earth-brand-tag">Pakistan</span>
          </div>
          <p className="text-sm text-slate-400 hidden sm:block">
            A clearer view of climate change
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
              className={`flex items-center gap-2 min-h-10 px-3 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                isActive
                ? "earth-nav-active shadow-sm border"
                : "earth-nav-idle"
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
          className="earth-status flex items-center gap-2 px-3 py-1.5 rounded-full border transition text-xs"
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
        <button
          onClick={() => setActiveTab("trends")}
          className="earth-header-action"
        >
          Explore the record <ArrowUpRight className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
