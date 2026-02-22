"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";
import { PlayerPropAnalysis } from "@/lib/api";

interface PlayerPropsProps {
  props: PlayerPropAnalysis[];
}

export default function PlayerProps({ props }: PlayerPropsProps) {
  if (!props || props.length === 0) {
    return (
      <div className="text-center text-slate-400 py-8">
        Nenhum prop disponível
      </div>
    );
  }

  return (
    <div className="rounded-md border border-slate-700">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Prop</TableHead>
            <TableHead>Linha</TableHead>
            <TableHead>Média</TableHead>
            <TableHead>Últimos 5</TableHead>
            <TableHead>Últimos 10</TableHead>
            <TableHead>Over %</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {props.map((prop, idx) => (
            <TableRow key={idx}>
              <TableCell className="font-medium capitalize">
                {prop.prop_type === "points"
                  ? "Pontos"
                  : prop.prop_type === "rebounds"
                  ? "Rebotes"
                  : prop.prop_type === "assists"
                  ? "Assistências"
                  : prop.prop_type}
              </TableCell>
              <TableCell>{prop.line}</TableCell>
              <TableCell>{prop.average.toFixed(1)}</TableCell>
              <TableCell>{prop.last_5_avg?.toFixed(1) ?? "-"}</TableCell>
              <TableCell>{prop.last_10_avg?.toFixed(1) ?? "-"}</TableCell>
              <TableCell
                className={
                  prop.over_rate > 50
                    ? "text-green-500 font-semibold"
                    : "text-red-500 font-semibold"
                }
              >
                {prop.over_rate.toFixed(1)}%
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
