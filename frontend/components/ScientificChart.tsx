"use client";

import React, { useState, useMemo } from "react";

export interface DataPoint {
  timestamp: string;
  value: number;
  lower_bound?: number | null;
  upper_bound?: number | null;
  trend_value?: number | null;
  is_prediction?: boolean;
}

interface ScientificChartProps {
  data: DataPoint[];
  title?: string;
  unit: string;
  yLabel?: string;
  showTrend?: boolean;
  showInterval?: boolean;
  forecastOriginTimestamp?: string | null;
  height?: number;
  highlightPoints?: { timestamp: string; label: string; color?: string }[];
  chartType?: "line" | "bars" | "seasonal";
}

export function ScientificChart({
  data,
  title,
  unit,
  yLabel,
  showTrend = true,
  showInterval = true,
  forecastOriginTimestamp = null,
  height = 360,
  highlightPoints = [],
  chartType = "line",
}: ScientificChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<DataPoint | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);

  // Margins for axes
  const margin = { top: 25, right: 35, bottom: 45, left: 65 };
  const width = 850;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Compute min/max
  const { xValues, yMin, yMax } = useMemo(() => {
    if (!data || data.length === 0) {
      return { xValues: [], yMin: 0, yMax: 100 };
    }

    const xVals = data.map((d) => d.timestamp);
    let min = Infinity;
    let max = -Infinity;

    for (const d of data) {
      if (d.value < min) min = d.value;
      if (d.value > max) max = d.value;
      if (showInterval) {
        if (d.lower_bound != null && d.lower_bound < min) min = d.lower_bound;
        if (d.upper_bound != null && d.upper_bound > max) max = d.upper_bound;
      }
      if (showTrend && d.trend_value != null) {
        if (d.trend_value < min) min = d.trend_value;
        if (d.trend_value > max) max = d.trend_value;
      }
    }

    // Add 8% padding to Y axis
    const range = max - min || 1;
    const paddedMin = min - range * 0.08;
    const paddedMax = max + range * 0.08;

    return { xValues: xVals, yMin: paddedMin, yMax: paddedMax };
  }, [data, showInterval, showTrend]);

  // Scales
  const getX = (index: number) => {
    if (data.length <= 1) return margin.left + innerWidth / 2;
    return margin.left + (index / (data.length - 1)) * innerWidth;
  };

  const getY = (val: number) => {
    const norm = (val - yMin) / (yMax - yMin || 1);
    return margin.top + innerHeight - norm * innerHeight;
  };

  // Build SVG path strings
  const { historicalPath, forecastPath, trendPath, intervalPath, originX } = useMemo(() => {
    if (!data || data.length === 0) {
      return { historicalPath: "", forecastPath: "", trendPath: "", intervalPath: "", originX: null };
    }

    let histD = "";
    let foreD = "";
    let trD = "";
    let originXCoord: number | null = null;

    // Interval area
    const intervalTop: [number, number][] = [];
    const intervalBottom: [number, number][] = [];

    let hasStartedFore = false;

    data.forEach((d, i) => {
      const x = getX(i);
      const y = getY(d.value);

      if (forecastOriginTimestamp && d.timestamp === forecastOriginTimestamp) {
        originXCoord = x;
      }

      if (d.is_prediction) {
        if (!hasStartedFore) {
          // Connect to the preceding point
          if (i > 0) {
            const prevX = getX(i - 1);
            const prevY = getY(data[i - 1].value);
            foreD = `M ${prevX.toFixed(1)},${prevY.toFixed(1)} L ${x.toFixed(1)},${y.toFixed(1)}`;
          } else {
            foreD = `M ${x.toFixed(1)},${y.toFixed(1)}`;
          }
          hasStartedFore = true;
        } else {
          foreD += ` L ${x.toFixed(1)},${y.toFixed(1)}`;
        }

        if (showInterval && d.lower_bound != null && d.upper_bound != null) {
          intervalTop.push([x, getY(d.upper_bound)]);
          intervalBottom.unshift([x, getY(d.lower_bound)]);
        }
      } else {
        if (histD === "") {
          histD = `M ${x.toFixed(1)},${y.toFixed(1)}`;
        } else {
          histD += ` L ${x.toFixed(1)},${y.toFixed(1)}`;
        }
      }

      if (showTrend && d.trend_value != null) {
        const ty = getY(d.trend_value);
        if (trD === "") {
          trD = `M ${x.toFixed(1)},${ty.toFixed(1)}`;
        } else {
          trD += ` L ${x.toFixed(1)},${ty.toFixed(1)}`;
        }
      }
    });

    let intArea = "";
    if (intervalTop.length > 0) {
      const first = intervalTop[0];
      intArea = `M ${first[0].toFixed(1)},${first[1].toFixed(1)}`;
      for (let j = 1; j < intervalTop.length; j++) {
        intArea += ` L ${intervalTop[j][0].toFixed(1)},${intervalTop[j][1].toFixed(1)}`;
      }
      for (let k = 0; k < intervalBottom.length; k++) {
        intArea += ` L ${intervalBottom[k][0].toFixed(1)},${intervalBottom[k][1].toFixed(1)}`;
      }
      intArea += " Z";
    }

    return {
      historicalPath: histD,
      forecastPath: foreD,
      trendPath: trD,
      intervalPath: intArea,
      originX: originXCoord,
    };
  }, [data, yMin, yMax, showTrend, showInterval, forecastOriginTimestamp, chartType]);

  const baselineY = getY(0);

  // Y-axis tick marks
  const yTicks = useMemo(() => {
    const ticks: number[] = [];
    const count = 5;
    for (let i = 0; i <= count; i++) {
      ticks.push(yMin + (i / count) * (yMax - yMin));
    }
    return ticks;
  }, [yMin, yMax]);

  // X-axis tick marks (every ~10-15% of points or major years)
  const xTicks = useMemo(() => {
    if (!data || data.length === 0) return [];
    const step = Math.max(1, Math.floor(data.length / 7));
    const result: { index: number; label: string }[] = [];
    for (let i = 0; i < data.length; i += step) {
      const d = data[i];
      // Format as YYYY-MM
      result.push({ index: i, label: d.timestamp.slice(0, 7) });
    }
    // Ensure final point is labeled if not close
    if (data.length > 0 && data.length - 1 - (result[result.length - 1]?.index || 0) > step / 2) {
      result.push({ index: data.length - 1, label: data[data.length - 1].timestamp.slice(0, 7) });
    }
    return result;
  }, [data]);

  // Mouse movement for tooltips
  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * width;
    const svgY = ((e.clientY - rect.top) / rect.height) * height;

    if (svgX < margin.left || svgX > width - margin.right) {
      setHoveredPoint(null);
      return;
    }

    // Find nearest point
    const relativeX = (svgX - margin.left) / innerWidth;
    const nearestIdx = Math.round(relativeX * (data.length - 1));
    const point = data[Math.max(0, Math.min(data.length - 1, nearestIdx))];

    if (point) {
      setHoveredPoint(point);
      setMousePos({ x: svgX, y: getY(point.value) });
    }
  };

  const handleMouseLeave = () => {
    setHoveredPoint(null);
    setMousePos(null);
  };

  if (!data || data.length === 0) {
    return (
      <div className="w-full flex items-center justify-center h-64 bg-slate-900/60 rounded-xl border border-slate-800 text-slate-400 text-sm">
        No time-series data available for the selected parameters.
      </div>
    );
  }

  return (
    <div className="relative w-full bg-slate-900/80 rounded-xl border border-slate-800/80 p-4 shadow-md">
      {title && (
        <div className="flex items-center justify-between mb-3 px-2">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold text-slate-100">{title}</h4>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
              {unit}
            </span>
          </div>

          {/* Interactive Legend */}
          <div className="flex items-center gap-4 text-xs text-slate-300">
            <div className="flex items-center gap-1.5">
              <span className={`w-3 ${chartType === "bars" ? "h-2 rounded-sm" : "h-0.5 rounded-full"} bg-blue-400`} />
              <span>{chartType === "seasonal" ? "Monthly average" : chartType === "bars" ? "Monthly anomaly" : "Observed"}</span>
            </div>
            {showTrend && trendPath && (
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-amber-400 border-dashed" />
                <span>Sen&apos;s Trend</span>
              </div>
            )}
            {forecastPath && (
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-emerald-400" />
                <span>Forecast</span>
              </div>
            )}
            {showInterval && intervalPath && (
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-2 bg-emerald-500/20 border border-emerald-500/40 rounded-sm" />
                <span>95% CI</span>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="w-full overflow-hidden">
        <svg
          role="img"
          aria-label={title ? `${title} chart` : `Time series chart showing values in ${unit}`}
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto cursor-crosshair select-none"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <defs>
            <linearGradient id="forecastAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
            </linearGradient>
            <linearGradient id="historyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {yTicks.map((tick, i) => {
            const y = getY(tick);
            return (
              <g key={`ytick-${i}`}>
                <line
                  x1={margin.left}
                  y1={y}
                  x2={width - margin.right}
                  y2={y}
                  stroke="#334155"
                  strokeDasharray="3 3"
                  strokeWidth="0.75"
                />
                <text
                  x={margin.left - 10}
                  y={y + 4}
                  textAnchor="end"
                  className="fill-slate-400 text-[10px] font-mono select-none"
                >
                  {tick.toFixed(tick < 10 && tick > -10 ? 2 : 1)}
                </text>
              </g>
            );
          })}

          {/* X ticks */}
          {xTicks.map((xt, i) => {
            const x = getX(xt.index);
            return (
              <g key={`xtick-${i}`}>
                <line
                  x1={x}
                  y1={margin.top + innerHeight}
                  x2={x}
                  y2={margin.top + innerHeight + 5}
                  stroke="#475569"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y={margin.top + innerHeight + 18}
                  textAnchor="middle"
                  className="fill-slate-400 text-[10px] font-mono select-none"
                >
                  {xt.label}
                </text>
              </g>
            );
          })}

          {/* Y Axis Label */}
          {yLabel && (
            <text
              transform={`rotate(-90)`}
              x={-(margin.top + innerHeight / 2)}
              y={18}
              textAnchor="middle"
              className="fill-slate-400 text-[11px] font-medium tracking-wide select-none"
            >
              {yLabel} ({unit})
            </text>
          )}

          {/* Forecast Uncertainty Shaded Band */}
          {showInterval && intervalPath && (
            <path
              d={intervalPath}
              fill="url(#forecastAreaGradient)"
              stroke="#10b981"
              strokeWidth="0.5"
              strokeOpacity="0.4"
            />
          )}

          {/* Sen's Trend Line */}
          {showTrend && trendPath && (
            <path
              d={trendPath}
              fill="none"
              stroke="#fbbf24"
              strokeWidth="2"
              strokeDasharray="5 3"
              strokeOpacity="0.9"
            />
          )}

          {/* Observed Historical Series */}
          {historicalPath && (chartType === "line" || chartType === "seasonal") && (
            <path
              d={historicalPath}
              fill="none"
              stroke={chartType === "seasonal" ? "#0f766e" : "#38bdf8"}
              strokeWidth={chartType === "seasonal" ? "3" : "2"}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          )}

          {chartType === "bars" && (
            <g>
              <line
                x1={margin.left}
                y1={baselineY}
                x2={width - margin.right}
                y2={baselineY}
                stroke="#64748b"
                strokeWidth="1"
              />
              {data.map((point, index) => {
                const x = getX(index);
                const y = getY(point.value);
                const barWidth = Math.max(1.5, Math.min(7, innerWidth / Math.max(data.length, 1) - 1));
                return (
                  <rect
                    key={`bar-${point.timestamp}`}
                    x={x - barWidth / 2}
                    y={Math.min(y, baselineY)}
                    width={barWidth}
                    height={Math.max(1, Math.abs(baselineY - y))}
                    fill={point.value >= 0 ? "#0f766e" : "#b45309"}
                    opacity="0.82"
                    rx="1"
                  />
                );
              })}
            </g>
          )}

          {/* Out-of-Sample Forecast Line */}
          {forecastPath && (
            <path
              d={forecastPath}
              fill="none"
              stroke="#10b981"
              strokeWidth="2.5"
              strokeDasharray="4 2"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          )}

          {/* Forecast Origin Demarcation Marker */}
          {originX != null && (
            <g>
              <line
                x1={originX}
                y1={margin.top}
                x2={originX}
                y2={margin.top + innerHeight}
                stroke="#a855f7"
                strokeWidth="1.5"
                strokeDasharray="3 3"
              />
              <text
                x={originX + 4}
                y={margin.top + 14}
                className="fill-purple-300 text-[9px] font-semibold"
              >
                Forecast Origin
              </text>
            </g>
          )}

          {/* Highlight Points (e.g. 2022 Monsoon Flooding anomaly) */}
          {highlightPoints.map((hp, idx) => {
            const ptIdx = data.findIndex((d) => d.timestamp.startsWith(hp.timestamp));
            if (ptIdx === -1) return null;
            const pt = data[ptIdx];
            const px = getX(ptIdx);
            const py = getY(pt.value);
            return (
              <g key={`hp-${idx}`}>
                <circle
                  cx={px}
                  cy={py}
                  r="5"
                  fill={hp.color || "#ef4444"}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
                <text
                  x={px}
                  y={py - 8}
                  textAnchor="middle"
                  className="fill-rose-300 text-[10px] font-bold"
                >
                  {hp.label}
                </text>
              </g>
            );
          })}

          {/* Hover Crosshair & Target Dot */}
          {hoveredPoint && mousePos && (
            <g>
              <line
                x1={mousePos.x}
                y1={margin.top}
                x2={mousePos.x}
                y2={margin.top + innerHeight}
                stroke="#94a3b8"
                strokeWidth="0.75"
                strokeDasharray="2 2"
              />
              <circle
                cx={mousePos.x}
                cy={mousePos.y}
                r="4.5"
                fill={hoveredPoint.is_prediction ? "#10b981" : "#38bdf8"}
                stroke="#0f172a"
                strokeWidth="2"
              />
            </g>
          )}
        </svg>
      </div>

      {/* Hover Tooltip Box */}
      {hoveredPoint && (
        <div className="earth-tooltip mt-2 flex flex-wrap items-center justify-between gap-3 px-3 py-2 border rounded-lg text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{hoveredPoint.timestamp}</span>
            <span
              className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                hoveredPoint.is_prediction
                  ? "earth-tooltip-forecast border"
                  : "earth-tooltip-observed border"
              }`}
            >
              {hoveredPoint.is_prediction ? "Forecast Projection" : "Observed Record"}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div>
              <span className="text-slate-400 mr-1.5">Value:</span>
              <span className="font-mono font-bold text-white">
                {hoveredPoint.value.toFixed(2)} {unit}
              </span>
            </div>

            {hoveredPoint.trend_value != null && (
              <div>
                <span className="text-amber-400/80 mr-1.5">Trend Fit:</span>
                <span className="font-mono text-amber-300">
                  {hoveredPoint.trend_value.toFixed(2)} {unit}
                </span>
              </div>
            )}

            {hoveredPoint.is_prediction &&
              hoveredPoint.lower_bound != null &&
              hoveredPoint.upper_bound != null && (
                <div>
                  <span className="text-emerald-400/80 mr-1.5">95% CI:</span>
                  <span className="font-mono text-emerald-300">
                    [{hoveredPoint.lower_bound.toFixed(2)}, {hoveredPoint.upper_bound.toFixed(2)}] {unit}
                  </span>
                </div>
              )}
          </div>
        </div>
      )}
    </div>
  );
}
