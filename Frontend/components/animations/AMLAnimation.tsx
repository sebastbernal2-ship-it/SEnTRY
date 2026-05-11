// components/animations/AMLAnimation.tsx
"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

// Counterparty graph: a payment fans out from the target wallet into many
// peripheral addresses, one of which routes into a known mixer. The mixer
// edge pulses red and the path is flagged. Conveys Problem 04 — AML detection.

const PERIPHERAL = [
  { x: 250, y: 40, label: "0x9f2A" },
  { x: 290, y: 80, label: "0xABCD" },
  { x: 270, y: 130, label: "0x5544" },
  { x: 240, y: 170, label: "0x9999" },
  { x: 200, y: 200, label: "0xCCCC" },
];

const MIXER = { x: 320, y: 130, label: "MIXER" };

export const AMLAnimation = () => {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setPulse((p) => (p + 1) % 4), 900);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      style={{
        width: "100%",
        padding: 12,
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
      aria-label="Anti-money-laundering graph visualization"
    >
      <div
        style={{
          fontFamily: "monospace",
          fontSize: 9,
          letterSpacing: "0.15em",
          color: "#475569",
          textTransform: "uppercase",
        }}
      >
        Counterparty topology
      </div>

      <svg viewBox="0 0 380 240" style={{ width: "100%", height: 200 }}>
        {/* Edges from source to peripheral addresses */}
        {PERIPHERAL.map((p, i) => (
          <line
            key={`edge-${i}`}
            x1={80}
            y1={120}
            x2={p.x}
            y2={p.y}
            stroke="#1e293b"
            strokeWidth={1}
          />
        ))}

        {/* Edge into mixer (red, pulsing) */}
        <motion.line
          x1={290}
          y1={80}
          x2={MIXER.x}
          y2={MIXER.y}
          stroke="#f87171"
          strokeWidth={2}
          animate={{ opacity: pulse % 2 === 0 ? 0.6 : 1 }}
          transition={{ duration: 0.45 }}
        />

        {/* Source wallet (user's agent) */}
        <g>
          <circle cx={80} cy={120} r={26} fill="#022c22" stroke="#22d3ee" strokeWidth={2} />
          <text
            x={80}
            y={124}
            textAnchor="middle"
            fontSize={10}
            fill="#22d3ee"
            fontFamily="monospace"
          >
            YOU
          </text>
        </g>

        {/* Peripheral nodes */}
        {PERIPHERAL.map((p, i) => (
          <g key={`node-${i}`}>
            <circle cx={p.x} cy={p.y} r={12} fill="#0f172a" stroke="#475569" strokeWidth={1} />
            <text
              x={p.x}
              y={p.y - 16}
              textAnchor="middle"
              fontSize={8}
              fill="#475569"
              fontFamily="monospace"
            >
              {p.label}
            </text>
          </g>
        ))}

        {/* Mixer node */}
        <motion.g
          animate={{ scale: pulse % 2 === 0 ? 1 : 1.08 }}
          transition={{ duration: 0.45 }}
          style={{ transformOrigin: `${MIXER.x}px ${MIXER.y}px`, transformBox: "fill-box" }}
        >
          <circle cx={MIXER.x} cy={MIXER.y} r={18} fill="#1a0505" stroke="#f87171" strokeWidth={2} />
          <text
            x={MIXER.x}
            y={MIXER.y + 4}
            textAnchor="middle"
            fontSize={9}
            fill="#f87171"
            fontFamily="monospace"
            fontWeight="bold"
          >
            MIXER
          </text>
        </motion.g>

        {/* Flag label on mixer edge */}
        <motion.g
          animate={{ opacity: pulse % 2 === 0 ? 0.4 : 1 }}
          transition={{ duration: 0.45 }}
        >
          <rect x={300} y={96} width={70} height={16} rx={2} fill="#0a0f1e" stroke="#f87171" strokeWidth={1} />
          <text
            x={335}
            y={107}
            textAnchor="middle"
            fontSize={8}
            fill="#f87171"
            fontFamily="monospace"
            letterSpacing={1}
          >
            AML BLOCK
          </text>
        </motion.g>
      </svg>
    </div>
  );
};
