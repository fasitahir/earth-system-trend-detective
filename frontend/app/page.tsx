"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  fetchHealth,
  fetchVariables,
  HealthStatus,
  VariableMeta,
  FALLBACK_VARIABLES,
} from "@/lib/api";
import { Navbar, ActiveTab } from "@/components/Navbar";
import { OverviewView } from "@/components/OverviewView";
import { TrendExplorerView } from "@/components/TrendExplorerView";
import { ForecastExplorerView } from "@/components/ForecastExplorerView";
import { GeographicView } from "@/components/GeographicView";
import { ReportsView } from "@/components/ReportsView";

export default function Home() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [selectedVariableId, setSelectedVariableId] = useState<string>("t2m");

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  const [variables, setVariables] = useState<VariableMeta[]>(FALLBACK_VARIABLES);
  const [varsLoading, setVarsLoading] = useState<boolean>(false);

  // Probe backend health
  const checkHealth = useCallback(async () => {
    try {
      setHealthLoading(true);
      const data = await fetchHealth();
      setHealth(data);
    } catch {
      setHealth({
        status: "disconnected",
        project_name: "EarthScope API",
        version: "0.1.0",
        environment: "local",
        timestamp: new Date().toISOString(),
      });
    } finally {
      setHealthLoading(false);
    }
  }, []);

  // Fetch variable catalog from backend
  const loadVariables = useCallback(async () => {
    try {
      setVarsLoading(true);
      const res = await fetchVariables();
      if (res && res.variables && res.variables.length > 0) {
        setVariables(res.variables);
      }
    } catch {
      // Keep verified fallback variables
      setVariables(FALLBACK_VARIABLES);
    } finally {
      setVarsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    loadVariables();
  }, [checkHealth, loadVariables]);

  const handleSelectVariableFromOverview = (varId: string, targetTab: ActiveTab) => {
    setSelectedVariableId(varId);
    setActiveTab(targetTab);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-emerald-500/30 selection:text-slate-100">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        loading={healthLoading}
        onRefreshHealth={checkHealth}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === "overview" && (
          <OverviewView
            variables={variables}
            onSelectVariable={handleSelectVariableFromOverview}
          />
        )}

        {activeTab === "trends" && (
          <TrendExplorerView
            variables={variables}
            selectedVariableId={selectedVariableId}
            onSelectVariable={setSelectedVariableId}
          />
        )}

        {activeTab === "forecast" && (
          <ForecastExplorerView
            variables={variables}
            selectedVariableId={selectedVariableId}
            onSelectVariable={setSelectedVariableId}
          />
        )}

        {activeTab === "geographic" && (
          <GeographicView
            variables={variables}
            onSelectVariable={handleSelectVariableFromOverview}
          />
        )}

        {activeTab === "reports" && <ReportsView variables={variables} />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 px-6 py-8 text-sm text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300">EarthScope</span>
            <span>NASA Space Apps Challenge 2026</span>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-slate-400">
            <span>NASA data through 2025</span>
            <span>Pakistan area averages</span>
            <span className="text-emerald-400 flex items-center gap-1">
              Data checked
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
