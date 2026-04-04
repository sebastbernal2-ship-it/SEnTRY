import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "S.E.N.T.R.Y.",
  description: "Secure ENgine for Transaction Risk & Yield-protection",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, background: "#020817", color: "#f8fafc" }}>
        {children}
      </body>
    </html>
  );
}