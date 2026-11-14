"use client";

import React from "react";
import {
  Sparkles,
  TrendingUp,
  Thermometer,
  CloudRain,
  Waves,
  Droplets,
  Layers,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Database,
  ExternalLink,
} from "lucide-react";
import { VariableMeta, FALLBACK_VARIABLES, FALLBACK_TRENDS } from "@/lib/api";
import { ActiveTab } from "./Navbar";

interface OverviewViewProps {
  variables: VariableMeta[];
  onSelectVariable: (varId: string, targetTab: ActiveTab) => void;
}

export function OverviewView({ variables, onSelectVariable }: OverviewViewProps) {
  const varsToDisplay = variables.length > 0 ? variables : FALLBACK_VARIABLES;

  const getVariableIcon = (id: string) => {
    switch (id) {
      case "t2m":
        return <Thermometer className="w-5 h-5 text-rose-400" />;
      case "ts":
        return <Thermometer className="w-5 h-5 text-amber-400" />;
      case "precipitation":
        return <CloudRain className="w-5 h-5 text-cyan-400" />;
      case "evapotranspiration":
        return <Waves className="w-5 h-5 text-blue-400" />;
      case "soil_moisture_0_10cm":
        return <Droplets className="w-5 h-5 text-emerald-400" />;
      case "soil_moisture_10_40cm":
        return <Layers className="w-5 h-5 text-teal-400" />;
      default:
        return <Database className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Hero Banner */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-6 sm:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            NASA Space Apps Challenge 2026 — Verified Giovanni Data Engine
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Scientific Earth System Trend Intelligence
          </h2>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            EarthScope delivers defensible historical trend quantification, seasonal climatology isolation, and honest out-of-sample machine learning forecasts across interconnected atmospheric and hydrological observation records.
          </p>

          <div className="pt-2 flex flex-wrap gap-4 text-xs text-slate-400">
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Area-Averaged Monthly Records (2001–2025)</span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Mann-Kendall & Yue-Pilon Prewhitening</span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Persisted Regularized ML Forecasts</span>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Reproducible Findings (Scientific Highlights) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">Featured Scientific Discoveries</h3>
          </div>
          <span className="text-xs text-slate-400">Reproducible findings from MERRA-2 & GLDAS</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Finding 1 */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-slate-700 transition">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-950/70 border border-amber-800/60 text-amber-300">
                Atmosphere & Land
              </span>
              <span className="text-xs font-mono text-slate-400">p = 0.0037</span>
            </div>
            <h4 className="text-sm font-bold text-white">
              Significant Land Surface Temperature Cooling Trend
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Sen&apos;s non-parametric slope reveals a statistically significant skin temperature decrease of{" "}
              <strong className="text-amber-300">-0.255 °C/decade</strong> across Pakistan (2001–2025), coupled with increased irrigation and agricultural greening.
            </p>
            <button
              onClick={() => onSelectVariable("ts", "trends")}
              className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium pt-1"
            >
              Inspect Skin Temp Trend <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Finding 2 */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-slate-700 transition">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-950/70 border border-cyan-800/60 text-cyan-300">
                Extreme Hydrology
              </span>
              <span className="text-xs font-mono text-rose-400 font-semibold">Z = +4.58</span>
            </div>
            <h4 className="text-sm font-bold text-white">
              Record 2022 Monsoon Flooding Anomaly
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              August 2022 recorded <strong className="text-cyan-300">118.8 mm/month</strong> precipitation against a climatological baseline of 43.1 mm (+75.7 mm anomaly), driving historic multi-province flooding and soil saturation.
            </p>
            <button
              onClick={() => onSelectVariable("precipitation", "trends")}
              className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium pt-1"
            >
              Analyze 2022 Monsoon Event <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Finding 3 */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-slate-700 transition">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950/70 border border-emerald-800/60 text-emerald-300">
                Hydrological Coupling
              </span>
              <span className="text-xs font-mono text-slate-400">r = 0.88</span>
            </div>
            <h4 className="text-sm font-bold text-white">
              Coordinated Soil Moisture & Evaporation Growth
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              GLDAS-2.1 root-zone moisture (+1.97 kg/m²/decade, p &lt; 0.001) strongly correlates with evapotranspiration (+3.32 mm/month/decade), indicating intensified terrestrial water recycling.
            </p>
            <button
              onClick={() => onSelectVariable("soil_moisture_10_40cm", "forecast")}
              className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium pt-1"
            >
              View Forecast Models <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* Environmental Variables Catalog */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white">Supported Earth System Variables</h3>
          </div>
          <span className="text-xs text-slate-400">{varsToDisplay.length} Available Datasets</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {varsToDisplay.map((v) => {
            const trend = FALLBACK_TRENDS[v.id];
            return (
              <div
                key={v.id}
                className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-slate-800 border border-slate-700/60">
                        {getVariableIcon(v.id)}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition">
                          {v.name}
                        </h4>
                        <span className="text-[10px] font-mono text-slate-400">{v.id}</span>
                      </div>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                      {v.display_unit}
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {v.description}
                  </p>

                  <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                    <div className="flex justify-between">
                      <span>Source Platform:</span>
                      <span className="text-slate-300 font-medium">{v.mission_source}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Coverage:</span>
                      <span className="text-slate-300 font-mono">
                        {v.start_date.slice(0, 4)} – {v.end_date.slice(0, 4)} ({v.total_months} mo)
                      </span>
                    </div>
                    {trend && (
                      <div className="flex justify-between">
                        <span>Sen&apos;s Slope:</span>
                        <span
                          className={`font-mono font-medium ${
                            trend.trend_direction === "increasing"
                              ? "text-emerald-400"
                              : trend.trend_direction === "decreasing"
                              ? "text-amber-400"
                              : "text-slate-400"
                          }`}
                        >
                          {trend.sen_slope_per_year != null
                            ? `${(trend.sen_slope_per_year * 10).toFixed(3)} ${trend.display_unit}`
                            : "N/A"}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-4 flex items-center gap-2">
                  <button
                    onClick={() => onSelectVariable(v.id, "trends")}
                    className="flex-1 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium flex items-center justify-center gap-1.5 transition"
                  >
                    <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
                    <span>Trends</span>
                  </button>
                  <button
                    onClick={() => onSelectVariable(v.id, "forecast")}
                    className="flex-1 py-1.5 px-3 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-800/60 text-emerald-300 text-xs font-medium flex items-center justify-center gap-1.5 transition"
                  >
                    <span>Forecast</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
