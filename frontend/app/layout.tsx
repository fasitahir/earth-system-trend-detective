import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EarthScope — Earth System Trend Intelligence",
  description: "NASA Space Apps Challenge 2026: Be an Earth System Trend Detective! Quantify, evaluate, and forecast Earth system trends with scientific rigor.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-slate-900 text-slate-100">
        {children}
      </body>
    </html>
  );
}
