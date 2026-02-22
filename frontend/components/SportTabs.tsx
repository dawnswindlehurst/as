"use client";

import { getSportById, getSportColorClass } from "@/lib/sports";

interface SportTabsProps {
  sports: string[];
  selectedSport: string;
  onSelectSport: (sport: string) => void;
}

export default function SportTabs({ sports, selectedSport, onSelectSport }: SportTabsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {sports.map((sportId) => {
        const sport = getSportById(sportId);
        const isSelected = selectedSport === sportId;
        const colorClass = getSportColorClass(sportId);
        
        return (
          <button
            key={sportId}
            onClick={() => onSelectSport(sportId)}
            className={`
              px-6 py-3 rounded-lg font-semibold transition-all whitespace-nowrap flex items-center gap-2
              ${isSelected 
                ? `bg-slate-700 border-2 ${colorClass}` 
                : "bg-slate-800 border-2 border-slate-700 text-slate-400 hover:bg-slate-700 hover:border-slate-600"
              }
            `}
          >
            {sport?.icon && <span className="text-xl">{sport.icon}</span>}
            <span>{sport?.name || sportId.toUpperCase()}</span>
          </button>
        );
      })}
    </div>
  );
}
