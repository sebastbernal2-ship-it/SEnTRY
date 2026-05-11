// components/animations/BehaviorAnimation.tsx
"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

// Five external agents send a stream of proposals to a central user agent.
// Each agent accumulates a behavior score over rolling windows; one agent
// gradually trips into "Manipulative" status as its score crosses a threshold.
// Conveys Problem 02 — Behavior-Based Manipulation Scoring.

type AgentRow = {
  id: string;
  label: string;
  baseScore: number;
  growth: number;
};

const AGENTS: AgentRow[] = [
  { id: "agent-A", label: "agent-7f2a", baseScore: 8, growth: 1 },
  { id: "agent-B", label: "agent-3c91", baseScore: 22, growth: 2 },
  { id: "agent-C", label: "agent-be40", baseScore: 5, growth: 0.5 },
  { id: "agent-D", label: "agent-d18e", baseScore: 38, growth: 8 },
  { id: "agent-E", label: "agent-44ff", baseScore: 14, growth: 1.5 },
];

const clamp = (n: number) => Math.max(0, Math.min(100, n));

export const BehaviorAnimation = () => {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => (t + 1) % 12), 700);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      style={{
        width: "100%",
        padding: 14,
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
      aria-label="Behavior manipulation scoring visualization"
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
        Rolling-window behavior scores
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {AGENTS.map((agent) => {
          const score = clamp(agent.baseScore + agent.growth * tick);
          const isHigh = score >= 70;
          const isMed = score >= 35 && !isHigh;
          const color = isHigh ? "#f87171" : isMed ? "#facc15" : "#22d3ee";
          return (
            <div
              key={agent.id}
              style={{
                display: "grid",
                gridTemplateColumns: "70px 1fr 30px",
                alignItems: "center",
                gap: 8,
                fontFamily: "monospace",
                fontSize: 10,
                color: "#94a3b8",
              }}
            >
              <span style={{ color: "#64748b" }}>{agent.label}</span>
              <div
                style={{
                  height: 6,
                  background: "#0f172a",
                  border: "1px solid #1e293b",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <motion.div
                  initial={false}
                  animate={{ width: `${score}%` }}
                  transition={{ duration: 0.5 }}
                  style={{
                    height: "100%",
                    background: color,
                    opacity: 0.85,
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    top: -2,
                    bottom: -2,
                    left: "70%",
                    width: 1,
                    background: "rgba(248,113,113,0.4)",
                  }}
                />
              </div>
              <span style={{ color, textAlign: "right" }}>{Math.round(score)}</span>
            </div>
          );
        })}
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontFamily: "monospace",
          fontSize: 8,
          color: "#475569",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          marginTop: 4,
        }}
      >
        <span>clean</span>
        <span style={{ color: "#facc15" }}>suspicious</span>
        <span style={{ color: "#f87171" }}>manipulative</span>
      </div>
    </div>
  );
};
