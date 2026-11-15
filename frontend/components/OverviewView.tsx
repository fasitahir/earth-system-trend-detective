"use client";

import React from "react";
import {
  ArrowRight,
  CloudRain,
  Database,
  Droplets,
  Layers,
  Thermometer,
  Waves,
} from "lucide-react";
import { VariableMeta, FALLBACK_VARIABLES, FALLBACK_TRENDS } from "@/lib/api";
import { ActiveTab } from "./Navbar";

interface OverviewViewProps {
  variables: VariableMeta[];
  onSelectVariable: (varId: string, targetTab: ActiveTab) => void;
}

const iconByVariable: Record<string, React.ReactNode> = {
  t2m: <Thermometer className="h-5 w-5" />,
  ts: <Thermometer className="h-5 w-5" />,
  precipitation: <CloudRain className="h-5 w-5" />,
  evapotranspiration: <Waves className="h-5 w-5" />,
  soil_moisture_0_10cm: <Droplets className="h-5 w-5" />,
  soil_moisture_10_40cm: <Layers className="h-5 w-5" />,
};

export function OverviewView({ variables, onSelectVariable }: OverviewViewProps) {
  const varsToDisplay = variables.length > 0 ? variables : FALLBACK_VARIABLES;

  return (
    <div className="earth-overview mx-auto max-w-7xl space-y-16 pb-16">
      <section className="earth-landing-hero">
        <div className="earth-hero-media" aria-hidden="true">
          <video
            className="earth-hero-video"
            autoPlay
            muted
            loop
            playsInline
            poster="https://svs.gsfc.nasa.gov/vis/a000000/a005200/a005259/PACE_EarthDay2024.03800_print.jpg"
          >
            <source
              src="https://svs.gsfc.nasa.gov/vis/a000000/a005200/a005259/PACE_EarthDay2024_1080p60.mp4"
              type="video/mp4"
            />
          </video>
        </div>
        <div className="earth-hero-overlay" aria-hidden="true" />
        <div className="earth-hero-copy">
          <p className="earth-kicker">NASA Earth science visualization for Pakistan from 2001 to 2025</p>
          <h2>Read Pakistan&apos;s climate as a landscape.</h2>
          <p className="earth-hero-lead">
            Temperature, rainfall, water in the soil, and evaporation brought
            together so the changes are easier to see.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => onSelectVariable("t2m", "trends")}
              className="earth-primary-action"
            >
              Explore temperature <ArrowRight className="h-4 w-4" />
            </button>
            <span className="earth-hero-note">NASA data for the Pakistan average</span>
          </div>
        </div>

      </section>

      <section className="earth-entry-section space-y-7">
        <div className="max-w-2xl">
          <h3 className="text-4xl">Three ways into the record</h3>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {[
            ["What changed?", "Follow the long-term pattern and see unusual months.", "trends", "t2m", "01"],
            ["What comes next?", "Ask the model for a forward view through a year you choose.", "forecast", "t2m", "02"],
            ["Where is it different?", "Compare Pakistan’s broad environmental zones.", "geographic", "precipitation", "03"],
          ].map(([title, description, tab, variable, number]) => (
            <article
              key={title}
              className="earth-entry-card group"
            >
              <span className="earth-entry-number">{number}</span>
              <span className="min-w-0 flex-1">
                <span className="block text-xl text-white">{title}</span>
                <span className="mt-2 block text-sm leading-6 text-slate-400">{description}</span>
              </span>
              <button
                onClick={() => onSelectVariable(variable, tab as ActiveTab)}
                className="earth-entry-action"
              >
                Explore <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="space-y-7">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-emerald-400">Choose a signal</p>
            <h3 className="mt-2 text-4xl">The records behind the story</h3>
          </div>
          <p className="text-sm text-slate-400">NASA Giovanni data, averaged across Pakistan</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {varsToDisplay.map((variable) => {
            const trend = FALLBACK_TRENDS[variable.id];
            const direction = trend?.trend_direction === "decreasing" ? "Down over time" : "Up over time";
            return (
              <article
                key={variable.id}
                className="flex min-h-56 flex-col justify-between rounded-[22px] border border-slate-800 bg-slate-900/60 p-6 shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between gap-4">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-950/80 text-emerald-400">
                      {iconByVariable[variable.id] || <Database className="h-5 w-5" />}
                    </span>
                    <span className="text-sm text-slate-400">{variable.display_unit}</span>
                  </div>
                  <h4 className="mt-6 text-2xl text-white">{variable.name}</h4>
                  <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-400">{variable.description}</p>
                </div>
                <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-sm">
                  <span className="text-slate-300">{direction}</span>
                  <button
                    onClick={() => onSelectVariable(variable.id, "trends")}
                    className="inline-flex min-h-10 items-center gap-1 rounded-full px-3 text-emerald-400 transition-colors hover:bg-emerald-950/80"
                  >
                    Explore <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="grid gap-8 border-t border-slate-800 pt-12 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <p className="text-sm font-medium text-emerald-400">A note on the numbers</p>
          <h3 className="mt-2 text-4xl">Clear first. Detailed when you need it.</h3>
        </div>
        <p className="max-w-2xl text-lg leading-8 text-slate-300">
          EarthScope uses NASA observations and tested statistical methods. You do not
          need to know the method names to use the result. Each view explains the
          conclusion first, with the calculation and source available underneath.
        </p>
      </section>
    </div>
  );
}
