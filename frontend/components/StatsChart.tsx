"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

interface StatsChartProps {
  title: string;
  data?: number[];
  labels?: string[];
}

export default function StatsChart({ title, data = [], labels = [] }: StatsChartProps) {
  const max = Math.max(...data, 1);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {data.map((value, idx) => {
            const percentage = (value / max) * 100;
            return (
              <div key={idx} className="flex items-center gap-2">
                <span className="text-sm text-slate-400 w-20 truncate">
                  {labels[idx] || `Item ${idx + 1}`}
                </span>
                <div className="flex-1 bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="text-sm font-medium w-12 text-right">
                  {value.toFixed(1)}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
