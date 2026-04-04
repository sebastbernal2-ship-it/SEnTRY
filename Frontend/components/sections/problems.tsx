// components/sections/problems.tsx
"use client";
import { PulseBeams } from "@/components/ui/pulse-beams";
import { ManipulationAnimation } from "@/components/animations/ManipulationAnimation";

const beams = [
  {
    path: "M0 200H300C305.523 200 310 204.477 310 210V434",
    gradientConfig: {
      initial: { x1: "0%", x2: "0%", y1: "0%", y2: "20%" },
      animate: { x1: ["0%", "0%", "100%"], x2: ["0%", "0%", "90%"], y1: ["0%", "100%", "100%"], y2: ["20%", "120%", "120%"] },
      transition: { duration: 3, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 1, delay: 0 },
    },
  },
  {
    path: "M858 100H600C594.477 100 590 104.477 590 110V434",
    gradientConfig: {
      initial: { x1: "100%", x2: "100%", y1: "0%", y2: "20%" },
      animate: { x1: ["100%", "0%", "0%"], x2: ["90%", "0%", "0%"], y1: ["0%", "0%", "100%"], y2: ["20%", "20%", "120%"] },
      transition: { duration: 3, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 1, delay: 1 },
    },
  },
];

const gradientColors = { start: "#18CCFC", middle: "#6344F5", end: "#AE48FF" };

const problems = [
  {
    id : "01",
    number: "01",
    title: "Anomaly Detection for Transactions",
    statement: "Autonomous on-chain agents operate continuously and at speed, making it impossible for users to manually review every transaction. Without a baseline of normal behavior, malicious or erroneous transactions — such as sudden large swaps or interactions with unknown contracts — go undetected until damage is done.",
  },
  {
    id : "02",
    number: "02",
    title: "Behavior-Based Manipulation Scoring",
    statement: "In multi-agent environments, a user's agent receives proposals and signals from many external agents, some of which may be adversarial. There is currently no systematic way to track whether an external agent is behaving suspiciously over time, leaving users vulnerable to coordinated manipulation campaigns that unfold gradually across many interactions.",
  },
  {
    id : "03",
    number: "03",
    title: "Prompt-Injection & Manipulation-Signal Detection",
    statement: "Agents that communicate via natural language are susceptible to text-based manipulation, where an adversarial agent embeds urgency cues, false guarantees, or deceptive framing into its messages to override the receiving agent's judgment. No lightweight, real-time filter exists at the message layer to catch this before it influences a transaction decision.",
  },
  {
    id : "04",
    number: "04",
    title: "Money Laundering Detection",
    statement: "When an autonomous agent executes payments on behalf of a user, it has no mechanism to assess whether the counterparty address is embedded in a laundering network. Interacting with such addresses exposes users to regulatory, reputational, and financial risk — risk that structured on-chain behavioral patterns could identify before a transaction is approved.",
  },
];

export const Problems = () => {
  return (
    <PulseBeams beams={beams} gradientColors={gradientColors} className="bg-[#020817]">
      <div style={{ minHeight: "100vh", padding: "120px 32px 80px", maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ marginBottom: 64 }}>
          <p style={{ fontSize: 11, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>
            The Challenge
          </p>
          <h2 style={{ fontSize: 28, fontWeight: 100, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase", margin: 0 }}>
            Problems
          </h2>
          <div style={{ width: 48, height: 1, background: "rgba(34,211,238,0.4)", marginTop: 16 }} />
        </div>

        {/* Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {problems.map((p) => (
            <div key={p.number} style={{
              border: "1px solid #1e293b", background: "rgba(15,23,42,0.2)",
              borderRadius: 2, padding: 32, display: "flex", gap: 32,
              transition: "border-color 0.3s ease",
            }}>
              {/* Left */}
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

              {/* Animation placeholder */}
              <div style={{
                width: 240,
                flexShrink: 0,
                border: "1px solid #1e293b",
                borderRadius: 2,
                background: "rgba(15,23,42,0.4)",
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
    </PulseBeams>
  );
};