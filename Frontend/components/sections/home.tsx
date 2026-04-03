// components/sections/home.tsx
"use client";
import { useState } from "react";
import { PulseBeams } from "@/components/ui/pulse-beams";
import { Zap, Shield } from "lucide-react";

const beams = [
  {
    path: "M269 220.5H16.5C10.9772 220.5 6.5 224.977 6.5 230.5V398.5",
    gradientConfig: {
      initial: { x1: "0%", x2: "0%", y1: "80%", y2: "100%" },
      animate: { x1: ["0%", "0%", "200%"], x2: ["0%", "0%", "180%"], y1: ["80%", "0%", "0%"], y2: ["100%", "20%", "20%"] },
      transition: { duration: 2, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 0.5 },
    },
    connectionPoints: [{ cx: 6.5, cy: 398.5, r: 6 }, { cx: 269, cy: 220.5, r: 6 }],
  },
  {
    path: "M568 200H841C846.523 200 851 195.523 851 190V40",
    gradientConfig: {
      initial: { x1: "0%", x2: "0%", y1: "80%", y2: "100%" },
      animate: { x1: ["20%", "100%", "100%"], x2: ["0%", "90%", "90%"], y1: ["80%", "80%", "-20%"], y2: ["100%", "100%", "0%"] },
      transition: { duration: 2, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 1 },
    },
    connectionPoints: [{ cx: 851, cy: 34, r: 6.5 }, { cx: 568, cy: 200, r: 6 }],
  },
  {
    path: "M425.5 274V333C425.5 338.523 421.023 343 415.5 343H152C146.477 343 142 347.477 142 353V426.5",
    gradientConfig: {
      initial: { x1: "0%", x2: "0%", y1: "80%", y2: "100%" },
      animate: { x1: ["20%", "100%", "100%"], x2: ["0%", "90%", "90%"], y1: ["80%", "80%", "-20%"], y2: ["100%", "100%", "0%"] },
      transition: { duration: 2, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 0 },
    },
    connectionPoints: [{ cx: 142, cy: 427, r: 6.5 }, { cx: 425.5, cy: 274, r: 6 }],
  },
  {
    path: "M493 274V333.226C493 338.749 497.477 343.226 503 343.226H760C765.523 343.226 770 347.703 770 353.226V427",
    gradientConfig: {
      initial: { x1: "40%", x2: "50%", y1: "160%", y2: "180%" },
      animate: { x1: "0%", x2: "10%", y1: "-40%", y2: "-20%" },
      transition: { duration: 2, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 1.5 },
    },
    connectionPoints: [{ cx: 770, cy: 427, r: 6.5 }, { cx: 493, cy: 274, r: 6 }],
  },
  {
    path: "M380 168V17C380 11.4772 384.477 7 390 7H414",
    gradientConfig: {
      initial: { x1: "-40%", x2: "-10%", y1: "0%", y2: "20%" },
      animate: { x1: ["40%", "0%", "0%"], x2: ["10%", "0%", "0%"], y1: ["0%", "0%", "180%"], y2: ["20%", "20%", "200%"] },
      transition: { duration: 2, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 0.8 },
    },
    connectionPoints: [{ cx: 420.5, cy: 6.5, r: 6 }, { cx: 380, cy: 168, r: 6 }],
  },
];

const gradientColors = { start: "#18CCFC", middle: "#6344F5", end: "#AE48FF" };

export const Home = ({ onNavigate }: { onNavigate: (s: string) => void }) => {
  const [connected, setConnected] = useState(false);
  const mockAddress = "0x3f5C...a91B";

  return (
    <PulseBeams beams={beams} gradientColors={gradientColors} className="bg-[#020817]">
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
          <Zap size={12} color="#22d3ee" />
          <span style={{ fontSize: 11, color: "#94a3b8", letterSpacing: "0.2em", textTransform: "uppercase" }}>
            AI-Powered Transaction Security
          </span>
        </div>

        {/* Title */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h1 style={{
            fontSize: "clamp(36px, 8vw, 80px)", fontWeight: 100,
            letterSpacing: "0.3em", color: "#fff", textTransform: "uppercase", margin: 0,
          }}>
            S.E.N.T.R.Y.
          </h1>
          <p style={{ fontSize: 11, letterSpacing: "0.2em", color: "#475569", textTransform: "uppercase" }}>
            Secure ENgine for Transaction Risk & Yield-protection
          </p>
        </div>

        {/* Description */}
        <p style={{ maxWidth: 420, fontSize: 13, color: "#94a3b8", lineHeight: 1.8, fontWeight: 300 }}>
          An AI security layer between your trading agent and the blockchain.
          Detect manipulation, flag anomalies, and block risky transactions before they hit the chain.
        </p>

        {/* CTA */}
        {!connected ? (
          <button
            onClick={() => setConnected(true)}
            style={{
              padding: "12px 32px", fontSize: 11, letterSpacing: "0.2em",
              textTransform: "uppercase", color: "#22d3ee",
              border: "1px solid rgba(34,211,238,0.3)", borderRadius: 2,
              background: "rgba(34,211,238,0.05)", cursor: "pointer",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={e => {
              (e.target as HTMLButtonElement).style.background = "rgba(34,211,238,0.1)";
              (e.target as HTMLButtonElement).style.borderColor = "rgba(34,211,238,0.6)";
            }}
            onMouseLeave={e => {
              (e.target as HTMLButtonElement).style.background = "rgba(34,211,238,0.05)";
              (e.target as HTMLButtonElement).style.borderColor = "rgba(34,211,238,0.3)";
            }}
          >
            Connect Wallet
          </button>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "8px 16px", border: "1px solid rgba(74,222,128,0.2)",
              background: "rgba(74,222,128,0.05)", borderRadius: 2,
            }}>
              <div style={{
                width: 6, height: 6, borderRadius: "50%", background: "#4ade80",
                animation: "pulse 2s infinite",
              }} />
              <span style={{ fontSize: 11, color: "#4ade80", letterSpacing: "0.15em" }}>{mockAddress}</span>
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
    </PulseBeams>
  );
};