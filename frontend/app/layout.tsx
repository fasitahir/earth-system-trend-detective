import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EarthScope | Climate changes in Pakistan",
  description: "Explore how temperature, rainfall, soil moisture, and evaporation have changed across Pakistan.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Funnel+Display:wght@300;400&family=Funnel+Sans:wght@400;500;700&display=swap"
        />
      </head>
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
