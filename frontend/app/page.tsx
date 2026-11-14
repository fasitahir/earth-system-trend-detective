"use client";

import { useEffect, useState } from "react";
import { fetchHealth, HealthStatus } from "@/lib/api";
import { Activity, CheckCircle2, AlertCircle, Database, Server, Compass, ShieldCheck } from "lucide-react";

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkBackend() {
      try {
        setLoading(true);
        const data = await fetchHealth();
        setHealth(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to reach backend");
      } finally {
        setLoading(false);
      }
    }
    checkBackend();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              EarthScope
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300">
                Stage 0 Initialized
              </span>
            </h1>
            <p className="text-xs text-slate-400">NASA Space Apps Challenge 2026: Be an Earth System Trend Detective!</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
            <span className={`w-2.5 h-2.5 rounded-full ${health?.status === "healthy" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
            <span className="font-medium text-slate-300">
              API: {loading ? "Connecting..." : health?.status === "healthy" ? "Connected (v0.1.0)" : "Disconnected"}
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 space-y-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-slate-900 via-slate-900/80 to-slate-950 border border-slate-800/80 rounded-2xl p-6 md:p-8 relative overflow-hidden">
          <div className="relative z-10 max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" /> Stage 0: Architecture & Foundation Complete
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight text-white">
              Scientific Earth-System Trend Intelligence
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              EarthScope provides defensible historical trend quantification, seasonal cycle filtering, and out-of-sample forecasting for interconnected climate and hydrological variables.
            </p>
          </div>
        </div>

        {/* Backend & Environment Health Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Backend Health</span>
              <Server className="w-4 h-4 text-slate-400" />
            </div>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Activity className="w-4 h-4 animate-spin text-blue-400" /> Checking API status...
              </div>
            ) : health ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-5 h-5" /> Operational
                </div>
                <div className="text-xs text-slate-400 space-y-1 pt-1 border-t border-slate-800/60">
                  <div className="flex justify-between"><span>Service:</span> <span className="text-slate-200">{health.project_name}</span></div>
                  <div className="flex justify-between"><span>Environment:</span> <span className="text-slate-200">{health.environment}</span></div>
                  <div className="flex justify-between"><span>Version:</span> <span className="text-slate-200">v{health.version}</span></div>
                  <div className="flex justify-between"><span>Data Access:</span> <span className="text-emerald-300">Verified ({health.components?.raw_data_accessible ? "Active" : "Unavailable"})</span></div>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-amber-400 font-semibold">
                  <AlertCircle className="w-5 h-5" /> Backend Unreachable
                </div>
                <p className="text-xs text-slate-400">{error || "Ensure FastAPI backend is running on port 8000."}</p>
              </div>
            )}
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Supplied Datasets</span>
              <Database className="w-4 h-4 text-slate-400" />
            </div>
            <div className="space-y-2">
              <div className="text-lg font-bold text-white">6 Variables (2001–2025)</div>
              <div className="text-xs text-slate-400 space-y-1">
                <div>• MERRA-2: 2m Air Temp & Surface Skin Temp</div>
                <div>• MERRA-2: Total Precipitation</div>
                <div>• GLDAS-2.1: Soil Moisture (0-10cm, 10-40cm)</div>
                <div>• GLDAS-2.1: Total Evapotranspiration</div>
                <div className="text-emerald-400 pt-1 font-medium">Region: Pakistan (Area-Averaged)</div>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Scientific Foundation</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="space-y-2">
              <div className="text-lg font-bold text-white">Defensible Pipeline</div>
              <div className="text-xs text-slate-400 space-y-1">
                <div>• Mann-Kendall & Sen&apos;s slope for monotonic trends</div>
                <div>• Seasonal decomposition & anomaly isolation</div>
                <div>• Chronological out-of-sample forecast validation</div>
                <div>• Clean separation: UI consumes backend API only</div>
              </div>
            </div>
          </div>
        </div>

        {/* Roadmap & Stage Status */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white">Stage-Gated Execution Roadmap</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-800/60 space-y-1">
              <span className="text-emerald-400 font-semibold">Stage 0: COMPLETE</span>
              <p className="text-slate-300">Foundation, Schemas, Health API, Test Harness</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-950/40 border border-blue-800/60 space-y-1">
              <span className="text-blue-400 font-semibold">Stage 1: NEXT UP</span>
              <p className="text-slate-300">Dataset Discovery & Quality Audit</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-400 font-semibold">Stages 2–3</span>
              <p className="text-slate-400">Ingestion, Pipeline & Exploratory Analysis</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-400 font-semibold">Stages 4–5</span>
              <p className="text-slate-400">Trend Statistics & Predictive Modeling</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        EarthScope • NASA Space Apps Challenge 2026 • Built with scientific rigor and reproducible evidence
      </footer>
    </main>
  );
}
