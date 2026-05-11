// components/animations/AnomalyAnimation.tsx
"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

// Stacked timeline of "normal" transactions with an occasional anomalous
// spike that flashes red and gets flagged by an autoencoder reconstruction
// trace overlay. Conveys Problem 01 — Anomaly Detection for Transactions.

type Bar = {
  id: number;
  height: number;
  anomaly: boolean;
};

const NORMAL_HEIGHTS = [22, 30, 26, 34, 28, 24, 32, 28, 26, 30, 28];

const buildBars = (anomalyIndex: number): Bar[] =>
  NORMAL_HEIGHTS.map((h, i) => ({
    id: i,
    height: i === anomalyIndex ? 78 : h,
    anomaly: i === anomalyIndex,
  }));

export const AnomalyAnimation = () => {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 2200);
    return () => clearInterval(id);
  }, []);

  const anomalyIndex = (tick % NORMAL_HEIGHTS.length + 4) % NORMAL_HEIGHTS.length;
  const bars = buildBars(anomalyIndex);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        gap: 8,
        padding: 16,
        boxSizing: "border-box",
      }}
      aria-label="Anomaly detection visualization"
    >
      <div
        style={{
          fontFamily: "monospace",
          fontSize: 9,
          letterSpacing: "0.15em",
          color: "#475569",
          textTransform: "uppercase",
        }}
      >
        Autoencoder reconstruction error
      </div>

      <svg viewBox="0 0 360 140" style={{ width: "100%", height: 140 }}>
        <line x1={8} y1={120} x2={352} y2={120} stroke="#1e293b" strokeWidth={1} />
        <line
          x1={8}
          y1={56}
          x2={352}
          y2={56}
          stroke="#1e293b"
          strokeWidth={1}
          strokeDasharray="4 4"
        />
        <text x={8} y={50} fontSize={8} fill="#475569" fontFamily="monospace">
          threshold
        </text>

        {bars.map((bar, i) => {
          const x = 16 + i * 30;
          const y = 120 - bar.height;
          const color = bar.anomaly ? "#f87171" : "#00FF41";
          return (
            <motion.rect
              key={`${tick}-${bar.id}`}
              x={x}
              y={y}
              width={20}
              height={bar.height}
              fill={color}
              opacity={bar.anomaly ? 0.95 : 0.55}
              initial={{ height: 4, y: 116 }}
              animate={{ height: bar.height, y }}
              transition={{ duration: 0.5, delay: i * 0.04 }}
            />
          );
        })}

        {bars.map((bar, i) => {
          if (!bar.anomaly) return null;
          const x = 16 + i * 30 + 10;
          return (
            <motion.g
              key={`flag-${tick}`}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <circle cx={x} cy={120 - bar.height - 10} r={5} fill="#f87171" />
              <text
                x={x}
                y={120 - bar.height - 16}
                textAnchor="middle"
                fontSize={9}
                fill="#f87171"
                fontFamily="monospace"
              >
                FLAG
              </text>
            </motion.g>
          );
        })}
      </svg>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontFamily: "monospace",
          fontSize: 9,
          color: "#475569",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}
      >
        <span>normal tx</span>
        <span style={{ color: "#f87171" }}>anomaly detected</span>
      </div>
    </div>
  );
};
