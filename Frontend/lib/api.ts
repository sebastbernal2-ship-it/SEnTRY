// Frontend/lib/api.ts

// TODO: change this to your deployed API URL when you deploy
const API_BASE_URL = "http://localhost:8000";

export interface Transaction {
  amount: number;
  token_type: number;
  hour: number;
  day_of_week: number;
  gas_fee: number;
  is_new_address: number;
  time_since_last_tx: number;
  tx_frequency: number;
}

export interface ScoreResponse {
  risk_score: number;
  label: string;
  reconstruction_error: number;
  threshold: number;
  features_used: Transaction;
}

export const scoreTransaction = async (transaction: Transaction): Promise<ScoreResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/anomaly/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(transaction),
  });
  if (!response.ok) throw new Error("Failed to score transaction");
  return response.json();
};

export const scoreBatch = async (transactions: Transaction[]): Promise<{ results: ScoreResponse[], count: number }> => {
  const response = await fetch(`${API_BASE_URL}/api/anomaly/score/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(transactions),
  });
  if (!response.ok) throw new Error("Failed to score batch");
  return response.json();
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.status === "healthy";
  } catch {
    return false;
  }
};

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

export const getRandomTransactions = async (): Promise<RandomTransaction[]> => {
  const response = await fetch(`${API_BASE_URL}/api/anomaly/random`);
  if (!response.ok) throw new Error("Failed to fetch random transactions");
  const data = await response.json();
  return data.transactions;
};

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

export const getExternalAgents = async (): Promise<ExternalAgent[]> => {
  const response = await fetch(`${API_BASE_URL}/api/manipulation/agents`);
  if (!response.ok) throw new Error("Failed to fetch manipulation agents");
  const data = await response.json();
  return data.agents;
};