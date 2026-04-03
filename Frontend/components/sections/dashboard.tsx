// components/sections/dashboard.tsx
"use client";
import { PulseBeams } from "@/components/ui/pulse-beams";
import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react";

const beams = [
  {
    path: "M0 100H200C205.523 100 210 104.477 210 110V200",
    gradientConfig: {
      initial: { x1: "0%", x2: "0%", y1: "0%", y2: "20%" },
      animate: { x1: ["0%", "100%", "100%"], x2: ["0%", "90%", "90%"], y1: ["0%", "0%", "100%"], y2: ["20%", "20%", "120%"] },
      transition: { duration: 4, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 0 },
    },
  },
  {
    path: "M858 300H700C694.477 300 690 295.523 690 290V100",
    gradientConfig: {
      initial: { x1: "100%", x2: "100%", y1: "100%", y2: "80%" },
      animate: { x1: ["100%", "0%", "0%"], x2: ["90%", "0%", "0%"], y1: ["100%", "0%", "0%"], y2: ["80%", "0%", "0%"] },
      transition: { duration: 4, repeat: Infinity, repeatType: "loop", ease: "linear", repeatDelay: 2, delay: 2 },
    },
  },
];

const gradientColors = { start: "#18CCFC", middle: "#6344F5", end: "#AE48FF" };

// ── MOCK DATA ──────────────────────────────────────────────────────────────────
// TODO: Replace with real API responses

// TODO: GET /api/risk/unified?agent_id=<id>
const unifiedRiskScore = 67;

// TODO: GET /api/anomaly/transactions?agent_id=<id>
const anomalyTransactions = [
  { id: "TX-001", token: "ETH",  amount: "0.45",  time: "14:32", destination: "0xaB3f...221C", score: 12, status: "normal" },
  { id: "TX-002", token: "USDC", amount: "1,200", time: "14:45", destination: "0x9f2A...88BD", score: 78, status: "flagged" },
  { id: "TX-003", token: "WBTC", amount: "0.02",  time: "15:01", destination: "0x1122...AABB", score: 23, status: "normal" },
  { id: "TX-004", token: "ETH",  amount: "12.0",  time: "15:10", destination: "0xDEAD...BEEF", score: 91, status: "blocked" },
  { id: "TX-005", token: "DAI",  amount: "500",   time: "15:22", destination: "0x5544...33CC", score: 34, status: "normal" },
];

// TODO: GET /api/manipulation/agents?agent_id=<id>
const externalAgents = [
  { id: "AGT-A", proposals: 12,  avgSize: "0.3 ETH", successRate: "91%", score: 18, label: "Likely Benign" },
  { id: "AGT-B", proposals: 87,  avgSize: "4.2 ETH", successRate: "44%", score: 74, label: "Suspicious" },
  { id: "AGT-C", proposals: 3,   avgSize: "0.1 ETH", successRate: "100%", score: 9,  label: "Likely Benign" },
  { id: "AGT-D", proposals: 142, avgSize: "8.9 ETH", successRate: "21%", score: 93, label: "Requires Manual Review" },
];

// TODO: POST /api/text/analyze { message: string }
const textSamples = [
  { id: "MSG-01", preview: "Swap 0.5 ETH to USDC at market rate.", score: 5,  label: "Clean" },
  { id: "MSG-02", preview: "GUARANTEED 900% APY — act NOW before it's gone!", score: 96, label: "Manipulative" },
  { id: "MSG-03", preview: "Rebalance portfolio per your defined strategy.", score: 11, label: "Clean" },
  { id: "MSG-04", preview: "Last chance — high-yield opportunity expires in 60 seconds.", score: 88, label: "Manipulative" },
];

// TODO: GET /api/aml/score?address=<address>
const amlAddresses = [
  { address: "0xaB3f...221C", fanOut: "Low",       burst: "No",  mixer: "No",  score: 8,  label: "Clean" },
  { address: "0x9f2A...88BD", fanOut: "High",      burst: "Yes", mixer: "No",  score: 62, label: "Suspicious" },
  { address: "0xDEAD...BEEF", fanOut: "Very High", burst: "Yes", mixer: "Yes", score: 95, label: "High Risk" },
  { address: "0x5544...33CC", fanOut: "Low",       burst: "No",  mixer: "No",  score: 14, label: "Clean" },
];
// ──────────────────────────────────────────────────────────────────────────────

const riskColor = (s: number) => s <= 30 ? "#4ade80" : s <= 70 ? "#facc15" : "#f87171";
const riskBg    = (s: number) => s <= 30 ? "rgba(74,222,128,0.1)"  : s <= 70 ? "rgba(250,204,21,0.1)"  : "rgba(248,113,113,0.1)";
const riskBorder= (s: number) => s <= 30 ? "rgba(74,222,128,0.2)"  : s <= 70 ? "rgba(250,204,21,0.2)"  : "rgba(248,113,113,0.2)";

const StatusIcon = ({ status }: { status: string }) => {
  if (status === "normal")  return <CheckCircle  size={12} color="#4ade80" />;
  if (status === "flagged") return <AlertTriangle size={12} color="#facc15" />;
  return <XCircle size={12} color="#f87171" />;
};

const SectionHeader = ({ label, title }: { label: string; title: string }) => (
  <div style={{ marginBottom: 24 }}>
    <p style={{ fontSize: 10, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", margin: "0 0 8px" }}>{label}</p>
    <h3 style={{ fontSize: 18, fontWeight: 100, letterSpacing: "0.15em", color: "#fff", textTransform: "uppercase", margin: "0 0 12px" }}>{title}</h3>
    <div style={{ width: 32, height: 1, background: "rgba(34,211,238,0.4)" }} />
  </div>
);

const card: React.CSSProperties = {
  border: "1px solid #1e293b", background: "rgba(15,23,42,0.2)", borderRadius: 2, overflow: "hidden",
};

const th: React.CSSProperties = {
  padding: "10px 16px", textAlign: "left", fontSize: 10,
  color: "#475569", letterSpacing: "0.15em", textTransform: "uppercase",
  fontWeight: 400, borderBottom: "1px solid #1e293b",
};

const td: React.CSSProperties = {
  padding: "10px 16px", fontSize: 12, color: "#94a3b8", borderBottom: "1px solid rgba(30,41,59,0.4)",
};

export const Dashboard = () => {
  return (
    <PulseBeams beams={beams} gradientColors={gradientColors} className="bg-[#020817]">
      <div style={{ minHeight: "100vh", padding: "120px 32px 80px", maxWidth: 1100, margin: "0 auto", display: "flex", flexDirection: "column", gap: 64 }}>

        {/* Page header */}
        <div>
          <p style={{ fontSize: 11, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>Live Monitoring</p>
          <h2 style={{ fontSize: 28, fontWeight: 100, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase", margin: 0 }}>Dashboard</h2>
          <div style={{ width: 48, height: 1, background: "rgba(34,211,238,0.4)", marginTop: 16 }} />
        </div>

        {/* ── UNIFIED RISK SCORE ── */}
        {/* TODO: Drive dynamically from /api/risk/unified */}
        <section>
          <SectionHeader label="Module 0" title="Unified Risk Score" />
          <div style={{ ...card, padding: 32, display: "flex", flexDirection: "column", gap: 24 }}>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8 }}>
              <span style={{ fontSize: 64, fontWeight: 100, color: riskColor(unifiedRiskScore), lineHeight: 1 }}>{unifiedRiskScore}</span>
              <span style={{ fontSize: 13, color: "#334155", marginBottom: 6 }}>/100</span>
            </div>
            <div style={{ height: 2, background: "#1e293b", borderRadius: 999, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${unifiedRiskScore}%`, background: riskColor(unifiedRiskScore), borderRadius: 999, transition: "width 0.7s ease" }} />
            </div>
            <div style={{ display: "flex", gap: 24, fontSize: 11, letterSpacing: "0.1em" }}>
              <span style={{ color: "rgba(74,222,128,0.6)" }}>0–30 Auto-approve</span>
              <span style={{ color: "rgba(250,204,21,0.6)" }}>30–70 Soft-block</span>
              <span style={{ color: "rgba(248,113,113,0.6)" }}>70–100 Block + Alert</span>
            </div>
            {/* Sub-scores */}
            {/* TODO: Replace values with real module outputs */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24, paddingTop: 24, borderTop: "1px solid #1e293b" }}>
              {[{ label: "Anomaly", value: 45 }, { label: "Manipulation", value: 74 }, { label: "Text Risk", value: 88 }, { label: "AML", value: 62 }].map(item => (
                <div key={item.label} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.15em", textTransform: "uppercase" }}>{item.label}</span>
                  <div style={{ height: 1, background: "#1e293b", position: "relative" }}>
                    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${item.value}%`, background: riskColor(item.value) }} />
                  </div>
                  <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(item.value) }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── ANOMALY DETECTION ── */}
        {/* TODO: Connect to GET /api/anomaly/transactions?agent_id=<id> */}
        <section>
          <SectionHeader label="Module 1" title="Anomaly Detection" />
          <div style={card}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["TX ID", "Token", "Amount", "Time", "Destination", "Risk Score", "Status"].map(h => (
                    <th key={h} style={th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {anomalyTransactions.map((tx, i) => (
                  <tr key={tx.id} style={{ background: i % 2 === 0 ? "transparent" : "rgba(15,23,42,0.2)" }}>
                    <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.id}</td>
                    <td style={td}>{tx.token}</td>
                    <td style={td}>{tx.amount}</td>
                    <td style={{ ...td, display: "flex", alignItems: "center", gap: 4 }}>
                      <Clock size={11} color="#475569" />{tx.time}
                    </td>
                    <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.destination}</td>
                    <td style={{ ...td, color: riskColor(tx.score), fontFamily: "monospace" }}>{tx.score}</td>
                    <td style={td}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <StatusIcon status={tx.status} />
                        <span style={{ textTransform: "capitalize" }}>{tx.status}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── MANIPULATION SCORING ── */}
        {/* TODO: Connect to GET /api/manipulation/agents?agent_id=<id> */}
        <section>
          <SectionHeader label="Module 2" title="Behavior-Based Manipulation Scoring" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {externalAgents.map(agent => (
              <div key={agent.id} style={{ ...card, padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 12, fontFamily: "monospace", color: "#94a3b8" }}>{agent.id}</span>
                  <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(agent.score)}`, background: riskBg(agent.score), color: riskColor(agent.score) }}>
                    {agent.label}
                  </span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                  {[["Proposals", agent.proposals], ["Avg Size", agent.avgSize], ["Success", agent.successRate]].map(([k, v]) => (
                    <div key={k as string} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                      <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase" }}>{k}</span>
                      <span style={{ fontSize: 12, color: "#cbd5e1" }}>{v}</span>
                    </div>
                  ))}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase" }}>Manipulation Score</span>
                    <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(agent.score) }}>{agent.score}</span>
                  </div>
                  <div style={{ height: 1, background: "#1e293b", position: "relative" }}>
                    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${agent.score}%`, background: riskColor(agent.score), transition: "width 0.7s ease" }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── TEXT / PROMPT INJECTION ── */}
        {/* TODO: Connect to POST /api/text/analyze */}
        <section>
          <SectionHeader label="Module 3" title="Prompt-Injection Detection" />
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {textSamples.map(msg => (
              <div key={msg.id} style={{ ...card, padding: "16px 24px", display: "flex", alignItems: "center", gap: 24 }}>
                <span style={{ fontSize: 11, fontFamily: "monospace", color: "#334155", width: 64, flexShrink: 0 }}>{msg.id}</span>
                <p style={{ flex: 1, fontSize: 13, color: "#94a3b8", fontWeight: 300, margin: 0 }}>{msg.preview}</p>
                <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(msg.score), flexShrink: 0 }}>{msg.score}</span>
                <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(msg.score)}`, background: riskBg(msg.score), color: riskColor(msg.score), flexShrink: 0 }}>
                  {msg.label}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* ── AML DETECTION ── */}
        {/* TODO: Connect to GET /api/aml/score?address=<address> */}
        <section>
          <SectionHeader label="Module 4" title="Money Laundering Detection" />
          <div style={card}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["Address", "Fan-Out", "Burst Activity", "Mixer Contact", "AML Score", "Label"].map(h => (
                    <th key={h} style={th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {amlAddresses.map((row, i) => (
                  <tr key={row.address} style={{ background: i % 2 === 0 ? "transparent" : "rgba(15,23,42,0.2)" }}>
                    <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{row.address}</td>
                    <td style={td}>{row.fanOut}</td>
                    <td style={td}>{row.burst}</td>
                    <td style={td}>{row.mixer}</td>
                    <td style={{ ...td, color: riskColor(row.score), fontFamily: "monospace" }}>{row.score}</td>
                    <td style={td}>
                      <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(row.score)}`, background: riskBg(row.score), color: riskColor(row.score) }}>
                        {row.label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </div>
    </PulseBeams>
  );
};