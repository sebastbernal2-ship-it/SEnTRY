// components/sections/about.tsx
"use client";
import { Shield } from "lucide-react";

const team = ["Nicolas", "Sebastian", "Dario"];

export const About = () => {
  return (
    <div style={{ position: "relative" }}>
      <div style={{ minHeight: "100vh", padding: "40px 32px 120px", maxWidth: 900, margin: "0 auto", display: "flex", flexDirection: "column", gap: 64 }}>

        {/* Header */}
        <div>
          <p style={{ fontSize: 11, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>Who We Are</p>
          <h2 style={{ fontSize: 28, fontWeight: 100, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase", margin: 0 }}>About</h2>
          <div style={{ width: 48, height: 1, background: "rgba(0,255,65,0.4)", marginTop: 16 }} />
        </div>

        {/* Mission */}
        <div style={{ border: "1px solid #1e293b", background: "rgba(0,0,0,0.6)", borderRadius: 2, padding: 32, display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Shield size={14} color="#00FF41" />
            <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase" }}>Mission</span>
          </div>
          <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.9, fontWeight: 300, margin: 0 }}>
            S.E.N.T.R.Y. is an AI-powered security layer built to protect autonomous on-chain agents from
            manipulation, anomalous behavior, and financial crime. As AI agents increasingly interact with
            blockchains and with each other, the attack surface grows in ways traditional tools were never
            designed to handle. We sit between your agent and the chain — scoring, flagging, and blocking
            threats before they cause irreversible damage.
          </p>
          <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.9, fontWeight: 300, margin: 0 }}>
            Our system combines transaction anomaly detection, multi-agent behavior profiling, natural language
            manipulation detection, and on-chain AML analysis into a single unified risk score — giving users
            and agents the situational awareness they need to operate safely.
          </p>
        </div>

        {/* Team */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div>
            <p style={{ fontSize: 10, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", margin: 0 }}>The Team</p>
            <div style={{ width: 32, height: 1, background: "rgba(0,255,65,0.4)", marginTop: 12 }} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
            {team.map(name => (
              <div key={name} style={{
                border: "1px solid #1e293b",
                background: "rgba(0,0,0,0.6)",
                borderRadius: 2, padding: 24,
                display: "flex", flexDirection: "column", gap: 16,
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: "50%",
                  border: "1px solid #1e293b", background: "rgba(0,255,65,0.05)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <span style={{ fontSize: 13, color: "#00FF41" }}>{name[0]}</span>
                </div>
                <span style={{ fontSize: 14, color: "#fff", fontWeight: 300, letterSpacing: "0.05em" }}>{name}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};