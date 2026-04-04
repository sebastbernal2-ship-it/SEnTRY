// components/sections/problems.tsx
"use client";

const problems = [
  {
    number: "01",
    title: "Anomaly Detection for Transactions",
    statement: "Autonomous on-chain agents operate continuously and at speed, making it impossible for users to manually review every transaction. Without a baseline of normal behavior, malicious or erroneous transactions — such as sudden large swaps or interactions with unknown contracts — go undetected until damage is done.",
  },
  {
    number: "02",
    title: "Behavior-Based Manipulation Scoring",
    statement: "In multi-agent environments, a user's agent receives proposals and signals from many external agents, some of which may be adversarial. There is currently no systematic way to track whether an external agent is behaving suspiciously over time, leaving users vulnerable to coordinated manipulation campaigns that unfold gradually across many interactions.",
  },
  {
    number: "03",
    title: "Prompt-Injection & Manipulation-Signal Detection",
    statement: "Agents that communicate via natural language are susceptible to text-based manipulation, where an adversarial agent embeds urgency cues, false guarantees, or deceptive framing into its messages to override the receiving agent's judgment. No lightweight, real-time filter exists at the message layer to catch this before it influences a transaction decision.",
  },
  {
    number: "04",
    title: "Money Laundering Detection",
    statement: "When an autonomous agent executes payments on behalf of a user, it has no mechanism to assess whether the counterparty address is embedded in a laundering network. Interacting with such addresses exposes users to regulatory, reputational, and financial risk — risk that structured on-chain behavioral patterns could identify before a transaction is approved.",
  },
];

import { ManipulationAnimation } from "@/components/animations/ManipulationAnimation";

export const Problems = () => {
  return (
    <div style={{ position: "relative" }}>
      <div style={{ minHeight: "100vh", padding: "120px 32px 80px", maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ marginBottom: 64 }}>
          <p style={{ fontSize: 11, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>
            The Challenge
          </p>
          <h2 style={{ fontSize: 28, fontWeight: 100, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase", margin: 0 }}>
            Problems
          </h2>
          <div style={{ width: 48, height: 1, background: "rgba(0,255,65,0.4)", marginTop: 16 }} />
        </div>

        {/* Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {problems.map((p) => (
            <div key={p.number} style={{
              border: "1px solid #1e293b",
              background: "rgba(0,0,0,0.6)",
              borderRadius: 2,
              padding: 32,
              display: "flex",
              gap: 32,
            }}>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 16 }}>
                <span style={{ fontSize: 11, color: "#334155", fontFamily: "monospace", letterSpacing: "0.1em" }}>
                  {p.number}
                </span>
                <h3 style={{ fontSize: 14, fontWeight: 300, letterSpacing: "0.1em", color: "#fff", margin: 0 }}>
                  {p.title}
                </h3>
                <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.8, fontWeight: 300, margin: 0 }}>
                  {p.statement}
                </p>
              </div>

              {/* TODO: Replace other placeholders with their animations */}
              <div style={{
                width: 240,
                flexShrink: 0,
                border: "1px solid #1e293b",
                borderRadius: 2,
                background: "rgba(0,0,0,0.4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                overflow: "hidden",
                minHeight: 160,
              }}>
                {p.number === "02" ? (
                  <ManipulationAnimation />
                ) : (
                  <span style={{ fontSize: 10, color: "#334155", letterSpacing: "0.15em", textTransform: "uppercase" }}>
                    Animation
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};