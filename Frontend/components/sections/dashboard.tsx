// components/sections/dashboard.tsx
"use client";
import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, XCircle, Clock, RefreshCw } from "lucide-react";
import {
  getTransactionAnomalies,
  AnomalyItem,
  getLatestAlerts,
  Alert,
  getPromptInjectionData,
  TextItem,
  getMoneyLaunderingData,
  AMLItem,
  getSummary,
  Summary,
} from "@/lib/api";



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

const TOP_RISK_ROWS = 10;
const LATEST_ROWS = 10;
const ALERT_THRESHOLD = 80;

export const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(false);

  // ── Fetch real data from JSON files ────────────────────────────────────────
  const [transactions, setTransactions] = useState<AnomalyItem[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [textMessages, setTextMessages] = useState<TextItem[]>([]);
  const [amlAddresses, setAmlAddresses] = useState<AMLItem[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);

  const fetchScores = async () => {
    setLoading(true);
    try {
      // Fetch all data in parallel
      const [
        txResults,
        alertResults,
        textResults,
        amlResults,
        summaryResults,
      ] = await Promise.all([
        getTransactionAnomalies(),
        getLatestAlerts(),
        getPromptInjectionData(),
        getMoneyLaunderingData(),
        getSummary(),
      ]);

      setTransactions(txResults);
      setAlerts(alertResults);
      setTextMessages(textResults);
      setAmlAddresses(amlResults);
      setSummary(summaryResults);
      setApiOnline(true);
    } catch (e) {
      console.error("Error fetching data", e);
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

  const manipulationAvg = alerts.length > 0
    ? Math.round(alerts.reduce((a, b) => a + b.score, 0) / alerts.length)
    : 0;

  const textAvg = textMessages.length > 0
    ? Math.round(textMessages.reduce((a, b) => a + b.risk_score, 0) / textMessages.length)
    : 0;

  const amlAvg = amlAddresses.length > 0
    ? Math.round(amlAddresses.reduce((a, b) => a + b.risk_score, 0) / amlAddresses.length)
    : 0;

  const unifiedRiskScore = Math.round((anomalyAvg + manipulationAvg + textAvg + amlAvg) / 4);
  const topRiskTransactions = [...transactions]
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, TOP_RISK_ROWS);
  const latestTransactions = transactions
    .slice(-LATEST_ROWS)
    .reverse()
    .slice(0, LATEST_ROWS);

  const transactionAlerts: Alert[] = transactions
    .filter((tx) => tx.risk_score >= ALERT_THRESHOLD)
    .map((tx) => ({
      id: `tx-alert-${tx.id}`,
      module: "transaction_anomaly",
      title: "Anomalous Transaction Behavior",
      description: `Transaction ${tx.id} flagged as anomalous (score: ${tx.risk_score})`,
      severity: tx.severity,
      score: tx.risk_score,
      label: tx.label,
      timestamp: summary?.updated_at || new Date().toISOString(),
    }));

  const dedupedAlertMap = new Map<string, Alert>();
  [...alerts, ...transactionAlerts].forEach((alert) => {
    const key = `${alert.module}:${alert.description}`;
    if (!dedupedAlertMap.has(key)) {
      dedupedAlertMap.set(key, alert);
    }
  });
  const combinedAlerts = [...dedupedAlertMap.values()].sort((a, b) => b.score - a.score);

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
              <span style={{ color: "rgba(250,204,21,0.6)" }}>30–80 Soft-block</span>
              <span style={{ color: "rgba(248,113,113,0.6)" }}>80–100 Block + Alert</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24, paddingTop: 24, borderTop: "1px solid #1e293b" }}>
              {[
                { label: "Anomaly",      value: anomalyAvg },
                { label: "Manipulation", value: manipulationAvg },
                { label: "Text Risk",    value: textAvg },
                { label: "AML",          value: amlAvg },
              ].map(item => (
                <div key={item.label} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <span style={{ fontSize: 10, color: "#475569", letterSpacing: "0.15em", textTransform: "uppercase" }}>{item.label}</span>
                  <div style={{ height: 1, background: "#1e293b", position: "relative" }}>
                    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: `${item.value}%`, background: riskColor(item.value) }} />
                  </div>
                  <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(item.value) }}>
                    {loading ? "..." : item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── MODULE 1A: TOP RISK TRANSACTIONS ── */}
        <section>
          <SectionHeader label="Module 1A — PyTorch Autoencoder" title="Top 10 Highest Risk Transactions" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading top risk transactions...
            </div>
          ) : (
            <div style={card}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>{["TX ID", "Amount", "Hour", "Risk Score", "Severity"].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {topRiskTransactions.map((tx, i) => (
                    <tr key={`risk-${tx.id}`} style={{ background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.2)" }}>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.id}</td>
                      <td style={td}>{tx.amount}</td>
                      <td style={{ ...td, display: "flex", alignItems: "center", gap: 4 }}>
                        <Clock size={11} color="#475569" />
                        {tx.hour}:00
                      </td>
                      <td style={{ ...td, color: riskColor(tx.risk_score), fontFamily: "monospace" }}>{tx.risk_score}</td>
                      <td style={td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <StatusIcon status={tx.severity} />
                          <span style={{ textTransform: "capitalize" }}>{tx.severity}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── MODULE 1B: LATEST TRANSACTIONS ── */}
        <section>
          <SectionHeader label="Module 1B — PyTorch Autoencoder" title="Latest 10 Transactions" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading latest transactions...
            </div>
          ) : (
            <div style={card}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>{["TX ID", "Amount", "Hour", "Risk Score", "Severity"].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {latestTransactions.map((tx, i) => (
                    <tr key={`latest-${tx.id}`} style={{ background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.2)" }}>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{tx.id}</td>
                      <td style={td}>{tx.amount}</td>
                      <td style={{ ...td, display: "flex", alignItems: "center", gap: 4 }}>
                        <Clock size={11} color="#475569" />
                        {tx.hour}:00
                      </td>
                      <td style={{ ...td, color: riskColor(tx.risk_score), fontFamily: "monospace" }}>{tx.risk_score}</td>
                      <td style={td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <StatusIcon status={tx.severity} />
                          <span style={{ textTransform: "capitalize" }}>{tx.severity}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── ALERTS ── */}
        <section>
          <SectionHeader label="Module 2" title="Alert Feed (All Transactions)" />
          {!loading && (
            <p style={{ margin: "0 0 12px", color: "#64748b", fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase" }}>
              Derived from full transaction set (risk score &gt;= {ALERT_THRESHOLD}) + pipeline alerts. Total matched: {combinedAlerts.length}
            </p>
          )}
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading alerts...
            </div>
          ) : (
            <div style={{ ...card, overflow: "hidden" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Module</th>
                    <th style={th}>Title</th>
                    <th style={th}>Description</th>
                    <th style={th}>Severity</th>
                    <th style={th}>Score</th>
                    <th style={th}>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {combinedAlerts.slice(0, 10).map(alert => (
                    <tr key={alert.id}>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{alert.module}</td>
                      <td style={td}>{alert.title}</td>
                      <td style={td}>{alert.description}</td>
                      <td style={{ ...td, color: riskColor(alert.score) }}>{alert.severity}</td>
                      <td style={{ ...td, fontFamily: "monospace", color: riskColor(alert.score) }}>{alert.score}</td>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                  {combinedAlerts.length === 0 && (
                    <tr>
                      <td style={td} colSpan={6}>No alerts in current dataset.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── TEXT / PROMPT INJECTION ── */}
        <section>
          <SectionHeader label="Module 3" title="Prompt-Injection Detection" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading prompt injection data...
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {textMessages.map(msg => (
                <div key={msg.id} style={{ ...card, padding: "16px 24px", display: "flex", alignItems: "center", gap: 24 }}>
                  <span style={{ fontSize: 11, fontFamily: "monospace", color: "#334155", width: 64, flexShrink: 0 }}>{msg.id}</span>
                  <p style={{ flex: 1, fontSize: 13, color: "#94a3b8", fontWeight: 300, margin: 0 }}>{msg.preview}</p>
                  <span style={{ fontSize: 12, fontFamily: "monospace", color: riskColor(msg.risk_score), flexShrink: 0 }}>{msg.risk_score}</span>
                  <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(msg.risk_score)}`, background: riskBg(msg.risk_score), color: riskColor(msg.risk_score), flexShrink: 0 }}>
                    {msg.label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── AML DETECTION ── */}
        <section>
          <SectionHeader label="Module 4" title="Money Laundering Detection" />
          {loading ? (
            <div style={{ ...card, padding: 32, textAlign: "center", color: "#475569", fontSize: 12 }}>
              Loading AML data...
            </div>
          ) : (
            <div style={card}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>{["Address", "Fan-Out", "Burst Activity", "Mixer Contact", "AML Score", "Label"].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {amlAddresses.map((row, i) => (
                    <tr key={row.address} style={{ background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.2)" }}>
                      <td style={{ ...td, fontFamily: "monospace", color: "#64748b" }}>{row.address}</td>
                      <td style={td}>{row.fan_out}</td>
                      <td style={td}>{row.burst_activity ? "Yes" : "No"}</td>
                      <td style={td}>{row.mixer_contact ? "Yes" : "No"}</td>
                      <td style={{ ...td, color: riskColor(row.risk_score), fontFamily: "monospace" }}>{row.risk_score}</td>
                      <td style={td}>
                        <span style={{ fontSize: 10, letterSpacing: "0.1em", padding: "3px 8px", borderRadius: 2, border: `1px solid ${riskBorder(row.risk_score)}`, background: riskBg(row.risk_score), color: riskColor(row.risk_score) }}>
                          {row.label}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

      </div>
    </div>
  );
};