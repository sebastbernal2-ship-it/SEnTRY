// components/sections/dashboard.tsx
"use client";
import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, XCircle, Clock, RefreshCw } from "lucide-react";
import { getRandomTransactions, RandomTransaction, getExternalAgents, ExternalAgent } from "@/lib/api";

// ── MOCK DATA for modules 2, 3, 4 ─────────────────────────────────────────────
// TODO: Replace with real API responses when those modules are built

// (Mock externalAgents removed in favor of live API integration)

const textSamples = [
  { id: "MSG-01", preview: "Swap 0.5 ETH to USDC at market rate.", score: 5,  label: "Clean" },
  { id: "MSG-02", preview: "GUARANTEED 900% APY — act NOW before it's gone!", score: 96, label: "Manipulative" },
  { id: "MSG-03", preview: "Rebalance portfolio per your defined strategy.", score: 11, label: "Clean" },
  { id: "MSG-04", preview: "Last chance — high-yield opportunity expires in 60 seconds.", score: 88, label: "Manipulative" },
];

const amlAddresses = [
  { address: "0xaB3f...221C", fanOut: "Low",       burst: "No",  mixer: "No",  score: 8,  label: "Clean" },
  { address: "0x9f2A...88BD", fanOut: "High",      burst: "Yes", mixer: "No",  score: 62, label: "Suspicious" },
  { address: "0xDEAD...BEEF", fanOut: "Very High", burst: "Yes", mixer: "Yes", score: 95, label: "High Risk" },
  { address: "0x5544...33CC", fanOut: "Low",       burst: "No",  mixer: "No",  score: 14, label: "Clean" },
];



const riskColor  = (s: number) => s <= 30 ? "#00FF41" : s <= 70 ? "#facc15" : "#f87171";
const riskBg     = (s: number) => s <= 30 ? "rgba(0,255,65,0.1)"   : s <= 70 ? "rgba(250,204,21,0.1)"  : "rgba(248,113,113,0.1)";
const riskBorder = (s: number) => s <= 30 ? "rgba(0,255,65,0.2)"   : s <= 70 ? "rgba(250,204,21,0.2)"  : "rgba(248,113,113,0.2)";

const StatusIcon = ({ status }: { status: string }) => {
  if (status === "normal")  return <CheckCircle  size={12} color="#00FF41" />;
  if (status === "flagged") return <AlertTriangle size={12} color="#facc15" />;
  return <XCircle size={12} color="#f87171" />;
};

const SectionHeader = ({ label, title }: { label: string; title: string }) => (
  <div style={{ marginBottom: 24 }}>
    <p style={{ fontSize: 10, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", margin: "0 0 8px" }}>{label}</p>
    <h3 style={{ fontSize: 18, fontWeight: 100, letterSpacing: "0.15em", color: "#fff", textTransform: "uppercase", margin: "0 0 12px" }}>{title}</h3>
    <div style={{ width: 32, height: 1, background: "rgba(0,255,65,0.4)" }} />
  </div>
);

const card: React.CSSProperties = {
  border: "1px solid #1e293b", background: "rgba(0,0,0,0.6)", borderRadius: 2, overflow: "hidden",
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
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(false);

  // ── Fetch real scores from API on mount ──────────────────────────────────
  const [transactions, setTransactions] = useState<RandomTransaction[]>([]);
  const [agents, setAgents] = useState<ExternalAgent[]>([]);

  const fetchScores = async () => {
    setLoading(true);
    try {
      const results = await getRandomTransactions();
      setTransactions(results);
      
      const agentResults = await getExternalAgents();
      setAgents(agentResults);
      
      setApiOnline(true);
    } catch (e) {
      console.error("API not reachable", e);
      setApiOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScores();
  }, []);


  // ── Unified risk score — average of all module scores ────────────────────
  const anomalyAvg = transactions.length > 0
    ? Math.round(transactions.reduce((a, b) => a + b.risk_score, 0) / transactions.length)
    : 0;

  const manipulationAvg = agents.length > 0 
    ? Math.round(agents.reduce((a, b) => a + b.risk_score, 0) / agents.length)
    : 74;

  const unifiedRiskScore = Math.round((anomalyAvg + manipulationAvg + 88 + 62) / 4);

  return (
    <div style={{ position: "relative" }}>
      <div style={{ minHeight: "100vh", padding: "80px 32px 120px", maxWidth: 1100, margin: "0 auto", display: "flex", flexDirection: "column", gap: 64 }}>

        {/* Page header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <p style={{ fontSize: 11, color: "#475569", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>Live Monitoring</p>
            <h2 style={{ fontSize: 28, fontWeight: 100, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase", margin: 0 }}>Dashboard</h2>
            <div style={{ width: 48, height: 1, background: "rgba(0,255,65,0.4)", marginTop: 16 }} />
          </div>
          {/* API status indicator */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: apiOnline ? "#00FF41" : "#f87171" }} />
            <span style={{ fontSize: 10, color: apiOnline ? "#00FF41" : "#f87171", letterSpacing: "0.15em", textTransform: "uppercase" }}>
              {apiOnline ? "API Online" : "API Offline"}
            </span>
            <button
              onClick={fetchScores}
              style={{ background: "transparent", border: "none", cursor: "pointer", padding: 4, color: "#475569" }}
            >
              <RefreshCw size={12} color="#475569" />
            </button>
          </div>
        </div>

        {/* ── UNIFIED RISK SCORE ── */}
        <section>
          <SectionHeader label="Module 0" title="Unified Risk Score" />
          <div style={{ ...card, padding: 32, display: "flex", flexDirection: "column", gap: 24 }}>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8 }}>
              <span style={{ fontSize: 64, fontWeight: 100, color: riskColor(unifiedRiskScore), lineHeight: 1 }}>
                {loading ? "..." : unifiedRiskScore}
              </span>
              <span style={{ fontSize: 13, color: "#334155", marginBottom: 6 }}>/100</span>
            </div>
            <div style={{ height: 2, background: "#1e293b", borderRadius: 999, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${unifiedRiskScore}%`, background: riskColor(unifiedRiskScore), borderRadius: 999 }} />
            </div>
            <div style={{ display: "flex", gap: 24, fontSize: 11, letterSpacing: "0.1em" }}>
              <span style={{ color: "rgba(0,255,65,0.6)" }}>0–30 Auto-approve</span>
              <span style={{ color: "rgba(250,204,21,0.6)" }}>30–70 Soft-block</span>
              <span style={{ color: "rgba(248,113,113,0.6)" }}>70–100 Block + Alert</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24, paddingTop: 24, borderTop: "1px solid #1e293b" }}>
              {[
                { label: "Anomaly",      value: anomalyAvg },
                { label: "Manipulation", value: manipulationAvg },
                { label: "Text Risk",    value: 88 },
                { label: "AML",          value: 62 },
              ].map(item => (
                <div key={item.label} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.15em", textTransform: "uppercase" }}>{item.label}</span>
                  <div style={{ height: 1, background: "#1e293b", position: "relative" }}>
                    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${item.value}%`, background: riskColor(item.value) }} />
                  </div>
                  <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(item.value) }}>
                    {(item.label === "Anomaly" || item.label === "Manipulation") ? (loading ? "..." : item.value) : item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── ANOMALY DETECTION — REAL API DATA ── */}
        <section>
          <SectionHeader label="Module 1 — PyTorch Autoencoder" title="Anomaly Detection" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading scores from API...
            </div>
          ) : (
            <div style={card}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>{["TX ID", "Token", "Amount", "Time", "Destination", "Risk Score", "Label"].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {transactions.map((tx, i) => (
                    <tr key={tx.id} style={{ background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.2)" }}>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.id}</td>
                      <td style={td}>{tx.token}</td>
                      <td style={td}>{tx.amount}</td>
                      <td style={{ ...td, display: "flex", alignItems: "center", gap: 4 }}>
                        <Clock size={11} color="#475569" />
                        {tx.time}
                      </td>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.destination}</td>
                      <td style={{ ...td, color: riskColor(tx.risk_score), fontFamily: "monospace" }}>{tx.risk_score}</td>
                      <td style={td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <StatusIcon status={tx.label} />
                          <span style={{ textTransform: "capitalize" }}>{tx.label}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── MANIPULATION SCORING ── */}
        <section>
          <SectionHeader label="Module 2" title="Behavior-Based Manipulation Scoring" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading agents from API...
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {agents.map(agent => (
                <div key={agent.agent_id} style={{ ...card, padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 12, fontFamily: "monospace", color: "#94a3b8" }}>{agent.agent_id}</span>
                    <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(agent.risk_score)}`, background: riskBg(agent.risk_score), color: riskColor(agent.risk_score) }}>
                      {agent.label}
                    </span>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                    {[
                      ["Proposals", agent.metrics.frequency], 
                      ["Avg Size", agent.metrics.avg_size.toFixed(2)], 
                      ["Success", (agent.metrics.success_rate * 100).toFixed(0) + "%"]
                    ].map(([k, v]) => (
                      <div key={k as string} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase" }}>{k}</span>
                        <span style={{ fontSize: 12, color: "#cbd5e1" }}>{v}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase" }}>Manipulation Score</span>
                      <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(agent.risk_score) }}>{agent.risk_score}</span>
                    </div>
                    <div style={{ height: 1, background: "#1e293b", position: "relative" }}>
                      <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${agent.risk_score}%`, background: riskColor(agent.risk_score) }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── TEXT / PROMPT INJECTION ── */}
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
        <section>
          <SectionHeader label="Module 4" title="Money Laundering Detection" />
          <div style={card}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>{["Address", "Fan-Out", "Burst Activity", "Mixer Contact", "AML Score", "Label"].map(h => <th key={h} style={th}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {amlAddresses.map((row, i) => (
                  <tr key={row.address} style={{ background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.2)" }}>
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
    </div>
  );
};