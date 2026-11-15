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
    <div className="mx-auto max-w-7xl space-y-16 pb-16">
      <section className="grid items-end gap-10 border-b border-slate-800 pb-12 pt-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="space-y-6">
          <p className="text-sm font-medium text-emerald-400">Pakistan, 2001 to 2025</p>
          <h2 className="max-w-3xl text-5xl leading-[0.98] sm:text-6xl">
            See how Pakistan&apos;s climate is changing.
          </h2>
          <p className="max-w-xl text-lg leading-8 text-slate-300">
            Explore temperature, rainfall, soil moisture, and evaporation in one calm,
            readable place. Start with a question, then follow the evidence.
          </p>
          <button
            onClick={() => onSelectVariable("t2m", "trends")}
            className="inline-flex min-h-11 items-center gap-2 rounded-full bg-emerald-950/80 px-5 text-sm font-medium text-emerald-300 shadow-sm transition-colors hover:bg-emerald-900/80"
          >
            Start with temperature <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        <div className="rounded-[22px] bg-slate-900/80 p-6 shadow-xl">
          <p className="text-sm text-slate-400">The short version</p>
          <p className="mt-4 max-w-md text-3xl leading-tight text-white">
            The clearest signal is in the air and on the ground.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-6 border-t border-slate-800 pt-5">
            <div>
              <p className="text-2xl font-bold text-emerald-400">24 years</p>
              <p className="mt-1 text-sm text-slate-400">of monthly records</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">6 signals</p>
              <p className="mt-1 text-sm text-slate-400">to compare side by side</p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-7">
        <div className="max-w-2xl">
          <p className="text-sm font-medium text-emerald-400">Three ways in</p>
          <h3 className="mt-8 text-4xl">What would you like to know?</h3>
        </div>
        <div className="grid gap-px overflow-hidden rounded-[22px] border border-slate-800 bg-slate-800">
          {[
            ["What changed?", "Follow the long-term pattern and see unusual months.", "trends", "t2m"],
            ["What comes next?", "Ask the model for a forward view through a year you choose.", "forecast", "t2m"],
            ["Where is it different?", "Compare Pakistan’s broad environmental zones.", "geographic", "precipitation"],
          ].map(([title, description, tab, variable]) => (
            <button
              key={title}
              onClick={() => onSelectVariable(variable, tab as ActiveTab)}
              className="group flex h-12 w-full items-center gap-5 bg-slate-950 px-4 py-2 text-left transition-colors hover:bg-slate-900"
            >
              <span className="w-8 shrink-0 text-sm text-emerald-400">
                0{title === "What changed?" ? "1" : title === "What comes next?" ? "2" : "3"}
              </span>
              <span className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between sm:gap-8">
                <span className="text-lg text-white">{title}</span>
                <span className="mt-1 block max-w-xl text-sm leading-6 text-slate-400 sm:mt-0">
                  {description}
                </span>
              </span>
              <ArrowRight className="h-4 w-4 shrink-0 text-emerald-400 transition-transform group-hover:translate-x-1" />
            </button>
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
