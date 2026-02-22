import type { Metadata } from "next";
import "../styles/globals.css";
import Navbar from "@/components/ui/Navbar";

export const metadata: Metadata = {
  title: "Capivara Bet - Esports Betting Analytics",
  description: "Sistema completo de apostas em esports com análise avançada",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="font-sans antialiased bg-slate-900 text-slate-50">
        <Navbar />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
