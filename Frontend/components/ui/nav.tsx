// components/ui/nav.tsx
"use client";
import { Shield } from "lucide-react";

interface NavProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

const navItems = [
  { id: "home", label: "Home" },
  { id: "problems", label: "Problems" },
  { id: "dashboard", label: "Dashboard" },
  { id: "about", label: "About" },
];

export const Nav = ({ activeSection, onNavigate }: NavProps) => {
  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 50,
      borderBottom: "1px solid rgba(30,41,59,0.5)",
      background: "rgba(2,8,23,0.85)",
      backdropFilter: "blur(12px)",
    }}>
      <div style={{
        maxWidth: 1100, margin: "0 auto", padding: "16px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div
          onClick={() => onNavigate("home")}
          style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}
        >
          <Shield size={18} color="#22d3ee" />
          <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: "0.2em", color: "#fff", textTransform: "uppercase" }}>
            S.E.N.T.R.Y.
          </span>
        </div>

        <div style={{ display: "flex", gap: 4 }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                position: "relative", padding: "8px 16px",
                fontSize: 11, letterSpacing: "0.15em", textTransform: "uppercase",
                background: activeSection === item.id ? "rgba(34,211,238,0.05)" : "transparent",
                border: activeSection === item.id ? "1px solid rgba(34,211,238,0.2)" : "1px solid transparent",
                color: activeSection === item.id ? "#22d3ee" : "#64748b",
                cursor: "pointer", borderRadius: 2,
                transition: "all 0.2s ease",
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};