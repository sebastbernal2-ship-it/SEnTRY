// app/page.tsx
"use client";
import { useState } from "react";
import { Nav } from "@/components/ui/nav";
import { MatrixCodeRain } from "@/components/ui/matrix-code-rain";
import { Home } from "@/components/sections/home";
import { Problems } from "@/components/sections/problems";
import { Dashboard } from "@/components/sections/dashboard";
import { About } from "@/components/sections/about";

export default function Page() {
  const [activeSection, setActiveSection] = useState("home");

  const renderSection = () => {
    switch (activeSection) {
      case "home": return <Home onNavigate={setActiveSection} />;
      case "problems": return <Problems />;
      case "dashboard": return <Dashboard />;
      case "about": return <About />;
      default: return <Home onNavigate={setActiveSection} />;
    }
  };

  return (
    <div style={{ background: "#000000", minHeight: "100vh", position: "relative", overflow: "hidden" }}>
      {/* Matrix rain sits behind everything */}
      <MatrixCodeRain
        textColor="#00FF41"
        fontSize={14}
        speed={0.3}
        density={1}
      />
      {/* Dark overlay to keep text readable — lighter in center */}
      <div style={{
        position: "fixed",
        inset: 0,
        zIndex: 1,
        background: "radial-gradient(ellipse at center, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.92) 100%)",
        pointerEvents: "none",
      }} />
      {/* All content sits above */}
      <div style={{ position: "relative", zIndex: 2 }}>
        <Nav activeSection={activeSection} onNavigate={setActiveSection} />
        {renderSection()}
      </div>
    </div>
  );
}