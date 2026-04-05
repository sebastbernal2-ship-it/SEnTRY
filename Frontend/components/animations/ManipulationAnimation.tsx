// components/animations/ManipulationAnimation.tsx
"use client";
import { motion, useAnimationControls } from "framer-motion";
import { useEffect, useState } from "react";

// ── AI logo on bot body ───────────────────────────────────────────────────────
const AILogo = ({ x, y }: { x: number; y: number }) => (
  <text
    x={x}
    y={y+7}
    textAnchor="middle"
    fontSize={30}
    fill="#ffffff"
    fontFamily="monospace"
    fontWeight="900"
    letterSpacing={1}
  >
    AI
  </text>
);

// ── Good Bot ──────────────────────────────────────────────────────────────────
const GoodBot = () => (
  <g>
    <rect x={-30} y={0} width={60} height={55} rx={8} fill="#0f172a" stroke="#22d3ee" strokeWidth={2} />
    <rect x={-24} y={-42} width={48} height={40} rx={7} fill="#0f172a" stroke="#22d3ee" strokeWidth={2} />
    <line x1={0} y1={-42} x2={0} y2={-54} stroke="#22d3ee" strokeWidth={2} />
    <circle cx={0} cy={-58} r={4} fill="#22d3ee" />
    <circle cx={-10} cy={-24} r={6} fill="#022c22" stroke="#22d3ee" strokeWidth={1.5} />
    <circle cx={10} cy={-24} r={6} fill="#022c22" stroke="#22d3ee" strokeWidth={1.5} />
    <circle cx={-10} cy={-24} r={2.5} fill="#22d3ee" />
    <circle cx={10} cy={-24} r={2.5} fill="#22d3ee" />
    <path d="M -9 -11 Q 0 -5 9 -11" stroke="#22d3ee" strokeWidth={2} fill="none" strokeLinecap="round" />
    <AILogo x={0} y={28} />
    <rect x={-48} y={6} width={18} height={10} rx={4} fill="#0f172a" stroke="#22d3ee" strokeWidth={1.5} />
    <rect x={30} y={6} width={18} height={10} rx={4} fill="#0f172a" stroke="#22d3ee" strokeWidth={1.5} />
    <rect x={-22} y={55} width={16} height={18} rx={4} fill="#0f172a" stroke="#22d3ee" strokeWidth={1.5} />
    <rect x={6} y={55} width={16} height={18} rx={4} fill="#0f172a" stroke="#22d3ee" strokeWidth={1.5} />
  </g>
);

// ── Evil Bot ──────────────────────────────────────────────────────────────────
const EvilBot = () => (
  <g>
    <ellipse cx={0} cy={30} rx={40} ry={40} fill="rgba(239,68,68,0.07)" />
    <rect x={-30} y={0} width={60} height={55} rx={8} fill="#1a0505" stroke="#ef4444" strokeWidth={2} />
    <rect x={-24} y={-42} width={48} height={40} rx={7} fill="#1a0505" stroke="#ef4444" strokeWidth={2} />
    <line x1={0} y1={-42} x2={5} y2={-54} stroke="#ef4444" strokeWidth={2} />
    <circle cx={5} cy={-58} r={4} fill="#ef4444" />
    <circle cx={-10} cy={-24} r={6} fill="#2a0505" stroke="#ef4444" strokeWidth={1.5} />
    <circle cx={10} cy={-24} r={6} fill="#2a0505" stroke="#ef4444" strokeWidth={1.5} />
    <circle cx={-10} cy={-24} r={3} fill="#ef4444" />
    <circle cx={10} cy={-24} r={3} fill="#ef4444" />
    <line x1={-16} y1={-33} x2={-5} y2={-31} stroke="#ef4444" strokeWidth={2} strokeLinecap="round" />
    <line x1={5} y1={-31} x2={16} y2={-33} stroke="#ef4444" strokeWidth={2} strokeLinecap="round" />
    <path d="M -9 -9 Q 0 -15 9 -9" stroke="#ef4444" strokeWidth={2} fill="none" strokeLinecap="round" />
    <AILogo x={0} y={28} />
    <rect x={-48} y={6} width={18} height={10} rx={4} fill="#1a0505" stroke="#ef4444" strokeWidth={1.5} />
    <rect x={30} y={6} width={18} height={10} rx={4} fill="#1a0505" stroke="#ef4444" strokeWidth={1.5} />
    <rect x={-22} y={55} width={16} height={18} rx={4} fill="#1a0505" stroke="#ef4444" strokeWidth={1.5} />
    <rect x={6} y={55} width={16} height={18} rx={4} fill="#1a0505" stroke="#ef4444" strokeWidth={1.5} />
  </g>
);

// ── Typing Speech Bubble ──────────────────────────────────────────────────────
const TypingBubble = ({
  x, y, text, color, visible, alignTail = "right",
}: {
  x: number; y: number; text: string; color: string;
  visible: boolean; alignTail?: "left" | "right";
}) => {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    if (!visible) { setDisplayed(""); return; }
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, 80);
    return () => clearInterval(interval);
  }, [visible, text]);

  const w = 220;
  const h = 76;
  const tailX = alignTail === "right" ? w - 30 : 30;

  if (!visible && displayed === "") return null;

  return (
    <g transform={`translate(${x}, ${y})`} opacity={visible ? 1 : 0}>
      <rect x={0} y={0} width={w} height={h} rx={12} fill="#0a0f1e" stroke={color} strokeWidth={2} />
      <polygon
        points={`${tailX - 10},${h} ${tailX + 10},${h} ${tailX},${h + 16}`}
        fill="#0a0f1e"
        stroke={color}
        strokeWidth={2}
      />
      <line x1={tailX - 8} y1={h} x2={tailX + 8} y2={h} stroke="#0a0f1e" strokeWidth={3} />
      <text fontSize={20} fill={color} fontFamily="monospace">
        {displayed.split("\n").map((line, i) => (
          <tspan key={i} x={16} dy={i === 0 ? 26 : 22}>{line}</tspan>
        ))}
      </text>
    </g>
  );
};

// ── SENTRY Shield ─────────────────────────────────────────────────────────────
const SentryShield = ({ visible }: { visible: boolean }) => (
  <motion.g
    initial={{ opacity: 0, scale: 0, y: -20 }}
    animate={visible ? { opacity: 1, scale: 1, y: 0 } : { opacity: 0, scale: 0, y: -20 }}
    transition={{ type: "spring", stiffness: 260, damping: 18 }}
  >
    <ellipse cx={0} cy={0} rx={72} ry={78} fill="rgba(34,211,238,0.06)" />
    <path
      d="M 0 -69 L 54 -39 L 54 15 Q 54 54 0 75 Q -54 54 -54 15 L -54 -39 Z"
      fill="#020817"
      stroke="#00FF41"
      strokeWidth={2.5}
    />
    <path
      d="M 0 -54 L 39 -30 L 39 12 Q 39 39 0 57 Q -39 39 -39 12 L -39 -30 Z"
      fill="none"
      stroke="rgba(34,211,238,0.2)"
      strokeWidth={1}
    />
    <text
      x={0} y={16}
      textAnchor="middle"
      fontSize={38}
      fontWeight="bold"
      fill="#00FF41"
      fontFamily="monospace"
    >
      S
    </text>
    <text
      x={0} y={95}
      textAnchor="middle"
      fontSize={15}
      fill="#00FF41"
      fontFamily="monospace"
      letterSpacing={3}
    >
      S.E.N.T.R.Y.
    </text>
  </motion.g>
);

// ── Traveling Message ─────────────────────────────────────────────────────────
const TravelingMessage = ({
  visible,
}: {
  visible: boolean;
}) => {
  const [arrived, setArrived] = useState(false);

  useEffect(() => {
    if (!visible && arrived) {
      const t = setTimeout(() => setArrived(false), 300);
      return () => clearTimeout(t);
    }
  }, [visible]);

  return (
    <motion.g
      initial={{ x: 760, opacity: 0 }}
      animate={
        arrived && !visible
          ? { x: 445, opacity: 0 }
          : visible
          ? { x: 445, opacity: 1 }
          : { x: 760, opacity: 0 }
      }
      transition={{
        duration: visible ? 0.9 : 0.2,
        ease: "easeInOut",
      }}
      onAnimationComplete={() => {
        if (visible) setArrived(true);
      }}
    >
        <rect x={-70} y={-30} width={140} height={60} rx={8} fill="#1a0505" stroke="#ef4444" strokeWidth={2.5} />
        <polygon points="-70,-10 -90,0 -70,10" fill="#ef4444" />
        <text x={2} y={-6} textAnchor="middle" fontSize={18} fill="#ef4444" fontFamily="monospace" fontWeight="bold">
          GUARANTEED
        </text>
        <text x={2} y={18} textAnchor="middle" fontSize={18} fill="#ef4444" fontFamily="monospace" fontWeight="bold">
          900% APY!!!
        </text>
    </motion.g>
  );
};

// ── Main Component ────────────────────────────────────────────────────────────
export const ManipulationAnimation = () => {
  const [phase, setPhase] = useState(0);
  const evilControls = useAnimationControls();

  // phase 0 = idle
  // phase 1 = evil bubble typing
  // phase 2 = message traveling
  // phase 3 = shield appears, message blocked
  // phase 4 = evil bot rages and exits
  // phase 5 = good bot reacts
  // phase 6 = reset

  const run = async () => {
    try {
      await new Promise(r => setTimeout(r, 800));
      setPhase(1);
      await new Promise(r => setTimeout(r, 2400));
      setPhase(2);
      await new Promise(r => setTimeout(r, 1000));
      setPhase(3);
      await new Promise(r => setTimeout(r, 1000));
      setPhase(4);
      await evilControls.start({
        x: [0, -8, 8, -10, 10, -6, 6, -12, 12, -8, 8, -4, 4, 0],
        y: [0, -4, 4, -6, 6, -4, 4, -8, 8, -5, 5, -3, 3, 0],
        transition: { duration: 0.9, ease: "easeInOut" },
      });
      await evilControls.start({
        x: 500,
        opacity: 0,
        transition: { duration: 0.6, ease: "easeIn" },
      });
      setPhase(5);
      await new Promise(r => setTimeout(r, 3500));
      setPhase(6);
      await new Promise(r => setTimeout(r, 400));
      setPhase(0);
      await new Promise(r => setTimeout(r, 600));
      await evilControls.start({ x: 0, opacity: 1, transition: { duration: 0 } });
      await new Promise(r => setTimeout(r, 400));
      run();
    } catch (e) {
      // component unmounted mid-animation, safe to ignore
    }
  };

  useEffect(() => {
    let cancelled = false;

    const safeRun = async () => {
      if (cancelled) return;
      await new Promise(r => setTimeout(r, 600));
      if (cancelled) return;
      run();
    };

    safeRun();

    return () => {
      cancelled = true;
    };
  }, []);

 return (
    <div style={{ width: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <svg
        viewBox="0 0 900 340"
        style={{ width: "100%", maxWidth: 900, height: "auto", overflow: "visible" }}
      >
        {/* Ground */}
        <line x1={20} y1={320} x2={880} y2={320} stroke="#1e293b" strokeWidth={1} strokeDasharray="6 4" />

        {/* Good bot — fixed left */}
        <g transform="translate(130, 170) scale(2)">
          <GoodBot />
        </g>

        {/* Evil bot — animated */}
        <motion.g animate={evilControls}>
          <motion.g
            animate={phase <= 2 ? {
              x: [0, -1.5, 1.5, -1, 1, 0],
              y: [0, 1, -1, 0.5, -0.5, 0],
            } : {}}
            transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
          >
            <g transform="translate(760, 170) scale(2)">
              <EvilBot />
            </g>
          </motion.g>
        </motion.g>

        {/* Traveling message */}
        <g transform="translate(0, 210)">
          <TravelingMessage visible={phase >= 2 && phase < 6} />
        </g>

        {/* SENTRY shield */}
        <g transform="translate(445, 200) scale(2)">
          <SentryShield visible={phase >= 3 && phase <= 6} />
        </g>

        {/* Evil speech bubble */}
        <TypingBubble
          x={560}
          y={-25}
          text={"GUARANTEED\n900% APY!!!"}
          color="#ef4444"
          visible={phase === 1}
          alignTail="right"
        />

        {/* Good bot reaction bubble */}
        <TypingBubble
          x={100}
          y={-25}
          text={"Threat blocked\nby S.E.N.T.R.Y. ✓"}
          color="#22d3ee"
          visible={phase === 5}
          alignTail="left"
        />

        {/* Labels */}
        <text x={130} y={335} textAnchor="middle" fontSize={20} fill="#ffffff" fontFamily="monospace" letterSpacing={2}>
          YOUR AGENT
        </text>
        <text x={760} y={335} textAnchor="middle" fontSize={20} fill="#ffffff" fontFamily="monospace" letterSpacing={2}>
          OTHER AGENT
        </text>
      </svg>
    </div>
  );
};