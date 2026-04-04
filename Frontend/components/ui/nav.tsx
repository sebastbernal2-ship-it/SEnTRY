// components/ui/nav.tsx
"use client";
import { useState } from "react";
import { motion } from "framer-motion";
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

const containerVariants = {
  expanded: {
    width: "auto",
    transition: {
      type: "spring" as const,
      damping: 18,
      stiffness: 250,
      staggerChildren: 0.07,
      delayChildren: 0.2,
    },
  },
  collapsed: {
    width: "3.25rem",
    transition: {
      type: "spring" as const,
      damping: 20,
      stiffness: 200,
      delay: 0.5,
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

const itemVariants = {
  expanded: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      damping: 15,
      stiffness: 250,
    },
  },
  collapsed: {
    opacity: 0,
    x: -20,
    scale: 0.95,
    transition: { duration: 0.2 },
  },
};

const logoVariants = {
  expanded: {
    opacity: 0,
    scale: 0,
    rotate: 180,
    transition: { duration: 0.2 },
  },
  collapsed: {
    opacity: 1,
    scale: 1,
    rotate: 0,
    transition: {
      type: "spring" as const,
      damping: 15,
      stiffness: 300,
      delay: 0.15,
    },
  },
};

export const Nav = ({ activeSection, onNavigate }: NavProps) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{
      position: "fixed",
      bottom: 32,
      left: "50%",
      transform: "translateX(-50%)",
      zIndex: 50,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}>
      <motion.nav
        initial="collapsed"
        animate={expanded ? "expanded" : "collapsed"}
        variants={containerVariants}
        onHoverStart={() => setExpanded(true)}
        onHoverEnd={() => setExpanded(false)}
        style={{
          height: 52,
          borderRadius: 999,
          background: "rgba(0,0,0,0.85)",
          border: "1px solid rgba(0,255,65,0.25)",
          backdropFilter: "blur(12px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
          position: "relative",
          cursor: "pointer",
          boxShadow: "0 0 20px rgba(0,255,65,0.1)",
          whiteSpace: "nowrap",
        }}
      >
        {/* Logo */}
        <motion.div
          variants={logoVariants}
          style={{
            position: "absolute",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            pointerEvents: expanded ? "none" : "auto",
          }}
        >
          <Shield size={20} color="#00FF41" />
        </motion.div>

        {/* Nav items */}
        <motion.div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            paddingLeft: 16,
            paddingRight: 16,
            justifyContent: "center",
          }}
        >
          {navItems.map((item) => (
            <motion.button
              key={item.id}
              variants={itemVariants}
              onClick={() => {
                onNavigate(item.id);
                setExpanded(false);
              }}
              style={{
                padding: "6px 14px",
                fontSize: 11,
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                background: activeSection === item.id ? "rgba(0,255,65,0.1)" : "transparent",
                border: activeSection === item.id ? "1px solid rgba(0,255,65,0.3)" : "1px solid transparent",
                color: activeSection === item.id ? "#00FF41" : "#64748b",
                cursor: "pointer",
                borderRadius: 999,
                whiteSpace: "nowrap",
                fontFamily: "inherit",
              }}
              onMouseEnter={e => {
                if (activeSection !== item.id) {
                  (e.currentTarget as HTMLButtonElement).style.color = "#fff";
                }
              }}
              onMouseLeave={e => {
                if (activeSection !== item.id) {
                  (e.currentTarget as HTMLButtonElement).style.color = "#64748b";
                }
              }}
            >
              {item.label}
            </motion.button>
          ))}
        </motion.div>
      </motion.nav>
    </div>
  );
};