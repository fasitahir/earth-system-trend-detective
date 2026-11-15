"use client";

import React, { useState, useEffect } from "react";
import {
  Globe2,
  MapPin,
  Compass,
  AlertTriangle,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Info,
  CheckCircle2,
  Mountain,
  Tractor,
  Droplets,
  Sun,
  ShieldCheck,
  Activity,
  Sliders,
} from "lucide-react";
import {
  VariableMeta,
  SpatialSummaryResponse,
  EcologicalZone,
  fetchSpatialSummary,
  FALLBACK_VARIABLES,
  FALLBACK_SPATIAL_SUMMARY,
} from "@/lib/api";
import { ActiveTab } from "./Navbar";

interface GeographicViewProps {
  variables: VariableMeta[];
  onSelectVariable: (varId: string, targetTab: ActiveTab) => void;
}

export function GeographicView({ variables, onSelectVariable }: GeographicViewProps) {
  const varsToUse = variables.length > 0 ? variables : FALLBACK_VARIABLES;

  const [spatialSummary, setSpatialSummary] = useState<SpatialSummaryResponse>(
    FALLBACK_SPATIAL_SUMMARY
  );
  const [selectedZoneId, setSelectedZoneId] = useState<string>("northern_highlands");
  const [activeVariableLayer, setActiveVariableLayer] = useState<string>("precipitation");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function loadSpatial() {
      setLoading(true);
      try {
        const res = await fetchSpatialSummary();
        if (isMounted) setSpatialSummary(res);
      } catch (err) {
        console.warn("Using fallback spatial summary:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadSpatial();
    return () => {
      isMounted = false;
    };
  }, []);

  const selectedZone =
    spatialSummary.zones.find((z) => z.id === selectedZoneId) || spatialSummary.zones[0];
  const activeTrend = spatialSummary.variable_trends.find(
    (t) => t.variable_id === activeVariableLayer
  );

  // SVG coordinate transformation for Pakistan Bounding Box:
  // Lat: 23.3125 to 37.6875 (height span ~ 14.375 deg)
  // Lon: 60.390625 to 77.734375 (width span ~ 17.34375 deg)
  const mapWidth = 500;
  const mapHeight = 440;
  const lonMin = 60.390625;
  const lonMax = 77.734375;
  const latMin = 23.3125;
  const latMax = 37.6875;

  const lonToSvgX = (lon: number) => {
    return 40 + ((lon - lonMin) / (lonMax - lonMin)) * (mapWidth - 80);
  };

  const latToSvgY = (lat: number) => {
    return 30 + ((latMax - lat) / (latMax - latMin)) * (mapHeight - 60);
  };

  // Representative boundary points of Pakistan (EPSG:4326)
  const boundaryPolygonPoints = [
    [75.0, 37.1],
    [76.8, 36.5],
    [77.7, 35.5],
    [75.8, 34.4],
    [74.5, 32.5],
    [75.0, 31.5],
    [73.5, 29.8],
    [71.5, 28.0],
    [71.0, 24.5],
    [68.2, 23.7],
    [66.8, 24.8],
    [63.5, 25.2],
    [61.5, 25.3],
    [60.9, 27.2],
    [61.8, 29.5],
    [63.3, 29.5],
    [66.5, 30.5],
    [69.5, 32.0],
    [71.0, 34.0],
    [72.5, 35.8],
    [74.0, 36.8],
  ];

  const polygonPathD =
    "M " +
    boundaryPolygonPoints
      .map(([lon, lat]) => `${lonToSvgX(lon).toFixed(1)},${latToSvgY(lat).toFixed(1)}`)
      .join(" L ") +
    " Z";

  const getZoneIcon = (id: string) => {
    switch (id) {
      case "northern_highlands":
        return <Mountain className="w-4 h-4 text-cyan-400" />;
      case "upper_indus":
        return <Tractor className="w-4 h-4 text-emerald-400" />;
      case "lower_indus":
        return <Droplets className="w-4 h-4 text-blue-400" />;
      case "western_plateau":
        return <Sun className="w-4 h-4 text-amber-400" />;
      case "coastal_zone":
        return <Globe2 className="w-4 h-4 text-teal-400" />;
      default:
        return <MapPin className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="earth-view space-y-8 max-w-7xl mx-auto pb-12">
      {/* Geospatial Header Banner */}
      <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <Globe2 className="w-3.5 h-3.5" />
          Stage 8: Geographic Intelligence & Spatial Integrity
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-1.5">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Pakistan Spatial Domain & Environmental Zones
            </h2>
            <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
              Spatial evaluation of NASA Giovanni observational series over Pakistan (State Dept 2017 polygon <code>shp_171</code>, WGS 84 / EPSG:4326), with ecological zone attribution and False Discovery Rate (FDR) significance adjustment.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-950 px-3 py-2 rounded-xl border border-slate-800 text-xs text-slate-300 font-mono">
            <span>Projection:</span>
            <span className="text-emerald-400 font-bold">EPSG:4326 (WGS 84)</span>
          </div>
        </div>

        {/* Bounding Coordinates Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-sm font-medium text-slate-400">North latitude</span>
            <p className="text-sm font-bold text-white font-mono mt-0.5">37.69° N</p>
            <span className="text-[10px] text-slate-400">Karakoram / Gilgit-Baltistan</span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-sm font-medium text-slate-400">South latitude</span>
            <p className="text-sm font-bold text-white font-mono mt-0.5">23.31° N</p>
            <span className="text-[10px] text-slate-400">Arabian Sea / Sindh Coast</span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-sm font-medium text-slate-400">West longitude</span>
            <p className="text-sm font-bold text-white font-mono mt-0.5">60.39° E</p>
            <span className="text-[10px] text-slate-400">Balochistan Border</span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-sm font-medium text-slate-400">East longitude</span>
            <p className="text-sm font-bold text-white font-mono mt-0.5">77.73° E</p>
            <span className="text-[10px] text-slate-400">Indus Basin / Punjab</span>
          </div>
        </div>
      </section>

      {/* Main Geographic Interactive Map & Zone Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive SVG Geographic Map (7 cols) */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Compass className="w-4 h-4 text-emerald-400" />
                <span>Spatial Domain & Observation Grid</span>
              </h3>
              <p className="text-xs text-slate-400">
                Click an ecological zone marker to inspect local climate mechanics
              </p>
            </div>

            {/* Variable Layer Selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Layer:</span>
              <select
                value={activeVariableLayer}
                onChange={(e) => setActiveVariableLayer(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
              >
                {varsToUse.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* SVG Map Canvas */}
          <div className="relative bg-slate-950/80 rounded-xl border border-slate-800/80 p-2 overflow-hidden flex items-center justify-center">
            <svg
              role="img"
              aria-label="Map of Pakistan showing environmental zones and selected climate layer"
              viewBox={`0 0 ${mapWidth} ${mapHeight}`}
              className="w-full h-auto select-none max-h-[460px]"
            >
              <defs>
                <linearGradient id="pakistanFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#059669" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#0284c7" stopOpacity="0.15" />
                </linearGradient>
                <pattern id="gridPattern" width="30" height="30" patternUnits="userSpaceOnUse">
                  <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" strokeWidth="0.5" />
                </pattern>
              </defs>

              {/* Background Grid Pattern */}
              <rect x="0" y="0" width={mapWidth} height={mapHeight} fill="url(#gridPattern)" />

              {/* Graticule Latitude lines */}
              {[24, 28, 32, 36].map((lat) => {
                const y = latToSvgY(lat);
                return (
                  <g key={`lat-${lat}`}>
                    <line x1="30" y1={y} x2={mapWidth - 30} y2={y} stroke="#334155" strokeDasharray="3 3" strokeWidth="0.5" />
                    <text x="25" y={y + 3} textAnchor="end" className="fill-slate-500 text-[9px]">
                      {lat}°N
                    </text>
                  </g>
                );
              })}

              {/* Graticule Longitude lines */}
              {[64, 68, 72, 76].map((lon) => {
                const x = lonToSvgX(lon);
                return (
                  <g key={`lon-${lon}`}>
                    <line x1={x} y1="20" x2={x} y2={mapHeight - 20} stroke="#334155" strokeDasharray="3 3" strokeWidth="0.5" />
                    <text x={x} y={mapHeight - 8} textAnchor="middle" className="fill-slate-500 text-[9px]">
                      {lon}°E
                    </text>
                  </g>
                );
              })}

              {/* Pakistan Country Polygon */}
              <path
                d={polygonPathD}
                fill="url(#pakistanFill)"
                stroke="#10b981"
                strokeWidth="2"
                strokeLinejoin="round"
                strokeOpacity="0.8"
              />

              {/* Marine Arabian Sea Indicator */}
              <text
                x={lonToSvgX(65.0)}
                y={latToSvgY(23.8)}
                className="fill-sky-500/50 text-[11px] font-semibold"
              >
                Arabian Sea
              </text>

              {/* Karakoram Cryosphere Indicator */}
              <text
                x={lonToSvgX(74.5)}
                y={latToSvgY(36.8)}
                className="fill-cyan-400/60 text-[10px] font-semibold"
              >
                Karakoram Cryosphere
              </text>

              {/* Ecological Zones Markers */}
              {spatialSummary.zones.map((zone) => {
                const px = lonToSvgX(zone.lon_center);
                const py = latToSvgY(zone.lat_center);
                const isSelected = zone.id === selectedZoneId;

                return (
                  <g
                    key={zone.id}
                    className="cursor-pointer transition-transform"
                    onClick={() => setSelectedZoneId(zone.id)}
                  >
                    {/* Pulsing ring for selected zone */}
                    {isSelected && (
                      <circle
                        cx={px}
                        cy={py}
                        r="14"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="1.5"
                        strokeOpacity="0.8"
                        className="animate-ping"
                      />
                    )}

                    <circle
                      cx={px}
                      cy={py}
                      r={isSelected ? "8" : "6"}
                      fill={isSelected ? "#10b981" : "#38bdf8"}
                      stroke="#0f172a"
                      strokeWidth="2"
                    />

                    <text
                      x={px}
                      y={py - 10}
                      textAnchor="middle"
                      className={`text-[10px] font-bold ${
                        isSelected ? "fill-emerald-300" : "fill-slate-300"
                      }`}
                    >
                      {zone.name.split(" ")[0]}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Active Layer Trend Badge */}
          {activeTrend && (
            <div className="earth-geo-contrast flex flex-wrap items-center justify-between gap-3 p-3 border rounded-xl text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">National Rate:</span>
                <span
                  className={`font-mono font-bold ${
                    activeTrend.trend_direction === "increasing"
                      ? "text-emerald-400"
                      : activeTrend.trend_direction === "decreasing"
                      ? "text-amber-400"
                      : "text-slate-300"
                  }`}
                >
                  {(activeTrend.sen_slope_per_decade > 0 ? "+" : "") +
                    activeTrend.sen_slope_per_decade.toFixed(3)}{" "}
                  {activeTrend.display_unit}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                  FDR q = {activeTrend.fdr_adjusted_p_value.toFixed(4)}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400 font-medium">
                  {activeTrend.is_significant ? "FDR Significant (α=0.05)" : "Not Significant"}
                </span>
                <button
                  onClick={() => onSelectVariable(activeTrend.variable_id, "trends")}
                  className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
                >
                  Inspect Series
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Selected Ecological Zone Details Drawer (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-slate-800 border border-slate-700/60">
                  {getZoneIcon(selectedZone.id)}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{selectedZone.name}</h4>
                  <span className="text-[10px] font-mono text-emerald-400">
                    {selectedZone.climate_classification}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {selectedZone.description}
            </p>

            <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Centroid Coordinates:</span>
                <span className="text-slate-200">
                  {selectedZone.lat_center}°N, {selectedZone.lon_center}°E
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Elevation Profile:</span>
                <span className="text-slate-200 font-mono">
                  {selectedZone.approx_elevation_m}
                </span>
              </div>
            </div>

            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-rose-300 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Vulnerability & Climate Mechanics:
              </span>
              <p className="text-xs text-slate-300 bg-rose-950/20 border border-rose-900/30 p-3 rounded-xl leading-relaxed">
                {selectedZone.vulnerability_profile}
              </p>
            </div>
          </div>

          {/* Quick Zone Switcher Buttons */}
          <div className="pt-2 border-t border-slate-800 space-y-2">
            <span className="text-sm font-medium text-slate-400">
              Switch Ecological Zone:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {spatialSummary.zones.map((z) => (
                <button
                  key={z.id}
                  onClick={() => setSelectedZoneId(z.id)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition ${
                    z.id === selectedZoneId
                      ? "bg-emerald-600 text-white font-semibold"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {z.name.split(" ")[0]}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Multiple-Testing Correction (FDR) & Scientific Integrity Section */}
      <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Spatial Multiple-Testing Correction & False Discovery Rate (FDR)</span>
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          When analyzing multiple Earth system indicators simultaneously across space, testing each variable at a nominal $\alpha = 0.05$ inflates the family-wise error rate. EarthScope applies the <strong>Benjamini-Hochberg (1995) procedure</strong> to control the False Discovery Rate across all 6 environmental time series:
        </p>

        <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/60 mt-2">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/80 text-slate-300 font-semibold border-b border-slate-700/80">
              <tr>
                <th className="py-2.5 px-3">Variable</th>
                <th className="py-2.5 px-3">Sen Slope / Decade</th>
                <th className="py-2.5 px-3">Nominal p-value</th>
                <th className="py-2.5 px-3">BH Adjusted q-value</th>
                <th className="py-2.5 px-3">FDR Status (α=0.05)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-200">
              {spatialSummary.variable_trends.map((t) => (
                <tr key={t.variable_id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3 font-semibold text-white">
                    {t.variable_name}
                    <span className="block text-[10px] font-mono text-slate-400">{t.variable_id}</span>
                  </td>
                  <td className="py-2.5 px-3 font-mono">
                    {(t.sen_slope_per_decade > 0 ? "+" : "") + t.sen_slope_per_decade.toFixed(3)}{" "}
                    {t.display_unit}
                  </td>
                  <td className="py-2.5 px-3 font-mono">
                    {t.p_value < 0.0001 ? "< 0.0001" : t.p_value.toFixed(4)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-cyan-300 font-semibold">
                    {t.fdr_adjusted_p_value < 0.0001
                      ? "< 0.0001"
                      : t.fdr_adjusted_p_value.toFixed(4)}
                  </td>
                  <td className="py-2.5 px-3">
                    {t.is_significant ? (
                      <span className="text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Significant
                      </span>
                    ) : (
                      <span className="text-slate-400">Not significant</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Spatial Granularity & Native Resolution Disclosure */}
      <section className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-5 space-y-3">
        <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-400" />
          <span>Observational Resolution & Spatial Boundaries Disclosure</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300 leading-relaxed">
          <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 space-y-1.5">
            <span className="font-semibold text-emerald-400">Native Sensor Resolutions:</span>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              <li>MERRA-2 Reanalysis (T2M, TS, PRECTOTCORR): 0.5° lat × 0.625° lon (~50 km × 60 km).</li>
              <li>GLDAS-2.1 Noah Land Surface Model: 0.25° lat × 0.25° lon (~25 km × 25 km).</li>
              <li>Area-averaging is weighted by cosine of latitude across the Pakistan boundary polygon.</li>
            </ul>
          </div>
          <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 space-y-1.5">
            <span className="font-semibold text-amber-400">Scientific Integrity Rule:</span>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              <li>No synthetic pixel-level spatial interpolation is manufactured.</li>
              <li>National polygon time-series are presented faithfully without inventing false geographic precision.</li>
              <li>Ecological zone descriptors contextualize how national averages relate to local topography.</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
