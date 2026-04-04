// components/sections/home.tsx
"use client";
import { useState } from "react";
import { TextScramble } from "@/components/ui/text-scramble";
import { Zap } from "lucide-react";

export const Home = ({ onNavigate }: { onNavigate: (s: string) => void }) => {
  const [connected, setConnected] = useState(false);
  const [scrambleTrigger, setScrambleTrigger] = useState(true);
  const [isScrambling, setIsScrambling] = useState(false);
  const mockAddress = "0x3f5C...a91B";

  const handleMouseEnter = () => {
    if (isScrambling) return;
    setIsScrambling(true);
    setScrambleTrigger(false);
    setTimeout(() => setScrambleTrigger(true), 50);
  };

  const handleScrambleComplete = () => {
    setIsScrambling(false);
  };

  return (
    <div style={{ position: "relative" }}>
      <div style={{
        minHeight: "100vh", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        gap: 32, padding: "0 24px", textAlign: "center",
      }}>
        {/* Badge */}
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          padding: "6px 14px", borderRadius: 999,
          border: "1px solid #1e293b", background: "rgba(15,23,42,0.5)",
        }}>
          <Zap size={12} color="#00FF41" />
          <span style={{ fontSize: 11, color: "#94a3b8", letterSpacing: "0.2em", textTransform: "uppercase" }}>
            AI-Powered Transaction Security
          </span>
        </div>

        {/* Title */}
        <div
          style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "center", cursor: "default" }}
          onMouseEnter={handleMouseEnter}
        >
          <TextScramble
            as="h1"
            duration={1.5}
            speed={0.04}
            characterSet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            trigger={scrambleTrigger}
            onScrambleComplete={handleScrambleComplete}
            style={{
              fontSize: "clamp(36px, 8vw, 80px)",
              fontWeight: 900,
              letterSpacing: "0.3em",
              color: "#fff",
              textTransform: "uppercase",
              margin: 0,
            }}
          >
            S.E.N.T.R.Y.
          </TextScramble>
          <p style={{ fontSize: 11, letterSpacing: "0.2em", color: "#475569", textTransform: "uppercase" }}>
            Secure ENgine for Transaction Risk & Yield-protection
          </p>
        </div>

        {/* Description */}
        <p style={{ maxWidth: 420, fontSize: 13, color: "#94a3b8", lineHeight: 1.8 }}>
          An AI security layer between your trading agent and the blockchain.
          Detect manipulation, flag anomalies, and block risky transactions before they hit the chain.
        </p>

        {/* CTA */}
        {!connected ? (
          <button
            onClick={() => setConnected(true)}
            style={{
              padding: "12px 32px", fontSize: 11, letterSpacing: "0.2em",
              textTransform: "uppercase", color: "#00FF41",
              border: "1px solid rgba(0,255,65,0.3)", borderRadius: 2,
              background: "rgba(0,255,65,0.05)", cursor: "pointer",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={e => {
              (e.target as HTMLButtonElement).style.background = "rgba(0,255,65,0.1)";
              (e.target as HTMLButtonElement).style.borderColor = "rgba(0,255,65,0.6)";
            }}
            onMouseLeave={e => {
              (e.target as HTMLButtonElement).style.background = "rgba(0,255,65,0.05)";
              (e.target as HTMLButtonElement).style.borderColor = "rgba(0,255,65,0.3)";
            }}
          >
            Connect Wallet
          </button>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "8px 16px", border: "1px solid rgba(0,255,65,0.2)",
              background: "rgba(0,255,65,0.05)", borderRadius: 2,
            }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#00FF41" }} />
              <span style={{ fontSize: 11, color: "#00FF41", letterSpacing: "0.15em" }}>
                {mockAddress}
              </span>
            </div>
            <button
              onClick={() => onNavigate("dashboard")}
              style={{
                padding: "12px 32px", fontSize: 11, letterSpacing: "0.2em",
                textTransform: "uppercase", color: "#f8fafc",
                border: "1px solid rgba(248,250,252,0.15)", borderRadius: 2,
                background: "rgba(248,250,252,0.05)", cursor: "pointer",
                transition: "all 0.3s ease",
              }}
            >
              Enter Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};