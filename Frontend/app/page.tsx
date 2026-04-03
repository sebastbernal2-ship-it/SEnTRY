// app/page.tsx
"use client";
import { useState } from "react";
import { Nav } from "@/components/ui/nav";
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
    <div style={{ background: "#020817", minHeight: "100vh" }}>
      <Nav activeSection={activeSection} onNavigate={setActiveSection} />
      {renderSection()}
    </div>
  );
}