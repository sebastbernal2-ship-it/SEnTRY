// Frontend/lib/api.ts

// API configuration
const API_BASE_URL = "http://localhost:8000";
const USE_JSON_DATA = true; // Set to false to use live API instead

// ─── Transaction Anomaly Detection ───────────────────────────────────────────

export interface Transaction {
  id: string;
  amount: number;
  token_type: number;
  hour: number;
  day_of_week: number;
  gas_fee: number;
  is_new_address: number;
  time_since_last_tx: number;
  tx_frequency: number;
}

export interface AnomalyItem extends Transaction {
  risk_score: number;
  label: string;
  severity: string;
}

export interface AnomalyData {
  module: string;
  updated_at: string;
  items: AnomalyItem[];
}

export const getTransactionAnomalies = async (): Promise<AnomalyItem[]> => {
  try {
    if (USE_JSON_DATA) {
      const response = await fetch("/data/transaction-anomaly.json");
      if (!response.ok) throw new Error("Failed to fetch anomalies");
      const data: AnomalyData = await response.json();
      return data.items || [];
    } else {
      // Fallback to API if available
      const response = await fetch(`${API_BASE_URL}/api/anomaly/batch`);
      if (!response.ok) throw new Error("API unavailable");
      return await response.json();
    }
  } catch (e) {
    console.error("Error fetching anomalies:", e);
    return [];
  }
};

// ─── Prompt Injection Detection ──────────────────────────────────────────────

export interface TextItem {
  id: string;
  preview: string;
  risk_score: number;
  label: string;
  severity: string;
}

export interface TextData {
  module: string;
  updated_at: string;
  items: TextItem[];
}

export const getPromptInjectionData = async (): Promise<TextItem[]> => {
  try {
    const response = await fetch("/data/prompt-injection.json");
    if (!response.ok) throw new Error("Failed to fetch prompt injection data");
    const data: TextData = await response.json();
    return data.items || [];
  } catch (e) {
    console.error("Error fetching prompt injection data:", e);
    return [];
  }
};

// ─── Money Laundering Detection ──────────────────────────────────────────────

export interface AMLItem {
  id: string;
  address: string;
  fan_out: string;
  burst_activity: boolean;
  mixer_contact: boolean;
  risk_score: number;
  label: string;
  severity: string;
}

export interface AMLData {
  module: string;
  updated_at: string;
  items: AMLItem[];
}

export const getMoneyLaunderingData = async (): Promise<AMLItem[]> => {
  try {
    const response = await fetch("/data/money-laundering.json");
    if (!response.ok) throw new Error("Failed to fetch AML data");
    const data: AMLData = await response.json();
    return data.items || [];
  } catch (e) {
    console.error("Error fetching AML data:", e);
    return [];
  }
};

// ─── Summary & Alerts ───────────────────────────────────────────────────────

export interface SummaryModule {
  key: string;
  title: string;
  flagged_count: number;
  total_count: number;
}

export interface Summary {
  updated_at: string;
  scan_status: string;
  modules: SummaryModule[];
}

export const getSummary = async (): Promise<Summary> => {
  try {
    const response = await fetch("/data/summary.json");
    if (!response.ok) throw new Error("Failed to fetch summary");
    return await response.json();
  } catch (e) {
    console.error("Error fetching summary:", e);
    return {
      updated_at: new Date().toISOString(),
      scan_status: "error",
      modules: [],
    };
  }
};

export interface Alert {
  id: string;
  module: string;
  title: string;
  description: string;
  severity: string;
  score: number;
  label: string;
  timestamp: string;
}

export interface AlertsData {
  updated_at: string;
  new_alert_count: number;
  alerts: Alert[];
}

export const getLatestAlerts = async (): Promise<Alert[]> => {
  try {
    const response = await fetch("/data/latest-alerts.json");
    if (!response.ok) throw new Error("Failed to fetch alerts");
    const data: AlertsData = await response.json();
    return data.alerts || [];
  } catch (e) {
    console.error("Error fetching alerts:", e);
    return [];
  }
};

// ─── Legacy API methods (kept for backward compatibility) ───────────────────

export interface RandomTransaction {
  id: string;
  token: string;
  amount: number;
  time: string;
  destination: string;
  risk_score: number;
  label: string;
  reconstruction_error: number;
}

export interface ExternalAgent {
  agent_id: string;
  risk_score: number;
  label: string;
  metrics: {
    frequency: number;
    avg_size: number;
    success_rate: number;
    volatility: number;
  };
}

export const getRandomTransactions = async (): Promise<RandomTransaction[]> => {
  try {
    const items = await getTransactionAnomalies();
    return items.map((item, idx) => ({
      id: item.id,
      token: ["ETH", "USDC", "DAI"][item.token_type % 3],
      amount: item.amount,
      time: `${item.hour}:00`,
      destination: `0x${Math.random().toString(16).slice(2, 8).toUpperCase()}...`,
      risk_score: item.risk_score,
      label: item.label,
      reconstruction_error: 0,
    }));
  } catch {
    return [];
  }
};

export const getExternalAgents = async (): Promise<ExternalAgent[]> => {
  try {
    const items = await getPromptInjectionData();
    return items.map((item, idx) => ({
      agent_id: `agent-${idx}`,
      risk_score: item.risk_score,
      label: item.label,
      metrics: {
        frequency: Math.random() * 100,
        avg_size: Math.random() * 50,
        success_rate: Math.random(),
        volatility: Math.random() * 0.5,
      },
    }));
  } catch {
    return [];
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    // Check if data files are accessible
    const response = await fetch("/data/summary.json");
    return response.ok;
  } catch {
    return false;
  }
};