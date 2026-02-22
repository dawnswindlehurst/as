"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { ESPORTS, TRADITIONAL_SPORTS } from "@/lib/sports";

export default function Navbar() {
  const pathname = usePathname();
  const [showSportsMenu, setShowSportsMenu] = useState(false);

  const links = [
    { href: "/", label: "Dashboard" },
    { href: "/games", label: "Jogos" },
    { href: "/props", label: "Player Props" },
    { href: "/value-bets", label: "Value Bets" },
    { href: "/validation", label: "📊 Validação" },
  ];

  return (
    <nav className="border-b border-slate-700 bg-slate-800">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <span className="text-xl font-bold text-white">Capivara Bet</span>
            </Link>

            <div className="hidden md:flex gap-6 items-center">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "text-sm font-medium transition-colors hover:text-blue-400",
                    pathname === link.href
                      ? "text-blue-400"
                      : "text-slate-300"
                  )}
                >
                  {link.label}
                </Link>
              ))}
              
              {/* Sports Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowSportsMenu(!showSportsMenu)}
                  className="text-sm font-medium text-slate-300 hover:text-blue-400 transition-colors flex items-center gap-1"
                >
                  Esportes
                  <span className="text-xs">▼</span>
                </button>
                
                {showSportsMenu && (
                  <div className="absolute top-full mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-lg z-50">
                    <div className="py-2">
                      {/* Esports Section */}
                      <div className="px-3 py-1 text-xs text-slate-500 font-semibold">
                        ESPORTS
                      </div>
                      {ESPORTS.map((sport) => (
                        <Link
                          key={sport.id}
                          href={`/games?sport=${sport.id}`}
                          className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                          onClick={() => setShowSportsMenu(false)}
                        >
                          <span className="mr-2">{sport.icon}</span>
                          {sport.name}
                        </Link>
                      ))}
                      
                      {/* Divider */}
                      <div className="my-2 border-t border-slate-700"></div>
                      
                      {/* Traditional Sports Section */}
                      <div className="px-3 py-1 text-xs text-slate-500 font-semibold">
                        TRADICIONAIS
                      </div>
                      {TRADITIONAL_SPORTS.map((sport) => (
                        <Link
                          key={sport.id}
                          href={`/games?sport=${sport.id}`}
                          className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                          onClick={() => setShowSportsMenu(false)}
                        >
                          <span className="mr-2">{sport.icon}</span>
                          {sport.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center">
              <span className="text-slate-300 text-sm">👤</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Close menu on outside click */}
      {showSportsMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSportsMenu(false)}
          role="button"
          tabIndex={0}
          aria-label="Close sports menu"
          onKeyDown={(e) => {
            if (e.key === 'Escape' || e.key === 'Enter') {
              setShowSportsMenu(false);
            }
          }}
        />
      )}
    </nav>
  );
}
