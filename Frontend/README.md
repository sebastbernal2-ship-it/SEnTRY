# S.E.N.T.R.Y. Dashboard
### Unified Security Visualization Framework

This is the official frontend interface for SEnTRY, providing real-time monitoring and visualization of the multi-module risk engine. The dashboard is designed to provide human operators and monitoring agents with immediate situational awareness of transaction risks, behavioral anomalies, and manipulation attempts.

---

## Core Features
*   **Unified Risk HUD**: A high-contrast monitoring interface that aggregates scores from the ML Anomaly, Behavioral Manipulation, NLP Detection, and AML modules.
*   **Real-Time Transaction Scoring**: Direct integration with the Backend API to visualize risk assessments for incoming and outgoing transactions.
*   **Interception Monitoring**: Specialized sections for tracking and explaining flagged or blocked transactions across all four security pillars.
*   **Agent Status Intelligence**: Visual indicators for API health and model readiness.

---

## Technical Architecture
*   **Framework**: Next.js 15 (App Router)
*   **Data Logic**: Direct asynchronous integration with SEnTRY Backend service.
*   **UI/UX**: Custom implementation using Tailwind CSS and Framer Motion for high-performance data visualization.
*   **Icons**: Standardized security iconography via Lucide React.

---

## Getting Started

### 1. Installation
Install the necessary dependencies within the Frontend directory:
```bash
npm install
```

### 2. Deployment
Start the Next.js development server:
```bash
npm run dev
```

### 3. Backend Connectivity
The frontend expects the SEnTRY Backend service to be accessible at `http://localhost:8000`. Ensure the backend API is active to enable live data streaming and scoring updates.

---

## Design Specifications
The dashboard utilizes a high-contrast monitor aesthetic (Obsidian/Green/Slate) to ensure data readability and focus. It follows a modular structure where each security pillar occupies a dedicated monitoring zone.
