"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { getValidationMetrics, ValidationMetrics } from "@/lib/api";

export default function ValidationPage() {
  const [metrics, setMetrics] = useState<ValidationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(7);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await getValidationMetrics(period);
        setMetrics(data);
      } catch (error) {
        console.error("Error fetching validation metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [period]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-slate-400 py-8">Carregando métricas...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-slate-400 py-8">
          Erro ao carregar métricas de validação
        </div>
      </div>
    );
  }

  const { overall, by_sport, by_market, equity_curve, calibration, insights, period: periodInfo } = metrics;

  // Helper function to get color based on value
  const getPerformanceColor = (value: number, isNegativeBad = true): string => {
    if (isNegativeBad) {
      if (value > 8) return "text-green-400";
      if (value > 0) return "text-blue-400";
      return "text-red-400";
    } else {
      if (value < -8) return "text-red-400";
      if (value < 0) return "text-blue-400";
      return "text-green-400";
    }
  };

  const getBorderColor = (value: number, isNegativeBad = true): string => {
    if (isNegativeBad) {
      if (value > 8) return "border-green-500";
      if (value > 0) return "border-blue-500";
      return "border-red-500";
    } else {
      if (value < -8) return "border-red-500";
      if (value < 0) return "border-blue-500";
      return "border-green-500";
    }
  };

  const getMedal = (rank: number): string => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return rank.toString();
  };

  const getInsightIcon = (type: string): string => {
    switch (type) {
      case "success": return "✅";
      case "warning": return "⚠️";
      case "info": return "ℹ️";
      case "danger": return "❌";
      default: return "•";
    }
  };

  const getInsightColor = (type: string): string => {
    switch (type) {
      case "success": return "border-green-500 bg-green-500/10";
      case "warning": return "border-yellow-500 bg-yellow-500/10";
      case "info": return "border-blue-500 bg-blue-500/10";
      case "danger": return "border-red-500 bg-red-500/10";
      default: return "border-slate-500 bg-slate-500/10";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          📊 Dashboard de Validação - Paper Trading
        </h1>
        <p className="text-slate-400">
          Período: {new Date(periodInfo.start).toLocaleDateString('pt-BR')} - {new Date(periodInfo.end).toLocaleDateString('pt-BR')} ({periodInfo.days} dias)
        </p>
      </div>

      {/* Period Selector */}
      <div className="mb-6 flex gap-2">
        {[7, 14, 30].map((days) => (
          <button
            key={days}
            onClick={() => setPeriod(days)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              period === days
                ? "bg-blue-500 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            {days} dias
          </button>
        ))}
      </div>

      {/* Overall Metrics - Top Row */}
      <div className="mb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="border-blue-500">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Total de Apostas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{overall.total_bets}</div>
              <p className="text-xs text-slate-500 mt-1">
                {overall.wins}W - {overall.losses}L
              </p>
            </CardContent>
          </Card>

          <Card className={`border-2 ${getBorderColor(overall.win_rate - 52.38)}`}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Win Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getPerformanceColor(overall.win_rate - 52.38)}`}>
                {overall.win_rate.toFixed(2)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">break-even: ~52.4%</p>
            </CardContent>
          </Card>

          <Card className={`border-2 ${getBorderColor(overall.roi)}`}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">ROI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getPerformanceColor(overall.roi)}`}>
                {overall.roi > 0 ? "+" : ""}{overall.roi.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">retorno sobre investimento</p>
            </CardContent>
          </Card>

          <Card className={`border-2 ${getBorderColor(overall.profit)}`}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Lucro/Prejuízo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getPerformanceColor(overall.profit)}`}>
                {overall.profit > 0 ? "+" : ""}R$ {overall.profit.toFixed(2)}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                de R$ {overall.total_wagered.toFixed(2)} apostados
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Overall Metrics - Bottom Row */}
      <div className="mb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className={`border-2 ${getBorderColor(overall.clv_average)}`}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                CLV Médio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getPerformanceColor(overall.clv_average)}`}>
                {overall.clv_average > 0 ? "+" : ""}{overall.clv_average.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">closing line value</p>
            </CardContent>
          </Card>

          <Card className="border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Sharpe Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {overall.sharpe_ratio.toFixed(2)}
              </div>
              <p className="text-xs text-slate-500 mt-1">risco ajustado</p>
            </CardContent>
          </Card>

          <Card className={`border-2 ${getBorderColor(overall.max_drawdown, false)}`}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Max Drawdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getPerformanceColor(overall.max_drawdown, false)}`}>
                {overall.max_drawdown.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">pior sequência</p>
            </CardContent>
          </Card>

          <Card className="border-slate-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Brier Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {calibration.brier_score.toFixed(2)}
              </div>
              <p className="text-xs text-slate-500 mt-1">calibração do modelo</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-white">📈 Equity Curve</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end gap-2">
              {equity_curve.map((point, index) => {
                const maxBankroll = Math.max(...equity_curve.map(p => p.bankroll));
                const minBankroll = Math.min(...equity_curve.map(p => p.bankroll));
                const range = maxBankroll - minBankroll || 1;
                const heightPercent = ((point.bankroll - minBankroll) / range) * 100;
                
                return (
                  <div key={point.date} className="flex-1 flex flex-col items-center gap-2">
                    <div className="relative w-full">
                      <div
                        className={`w-full rounded-t transition-all ${
                          point.profit >= 0 ? "bg-green-500" : "bg-red-500"
                        }`}
                        style={{ height: `${Math.max(heightPercent, 10)}%` }}
                      />
                    </div>
                    <div className="text-xs text-slate-400 rotate-45 origin-top-left">
                      {new Date(point.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 text-center text-sm text-slate-400">
              Evolução do bankroll ao longo do período
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance by Sport and Market */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Performance by Sport */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-white">
              🏆 Performance por Esporte
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-slate-700">
                  <tr>
                    <th className="text-left p-3 text-slate-400 font-medium">Rank</th>
                    <th className="text-left p-3 text-slate-400 font-medium">Esporte</th>
                    <th className="text-right p-3 text-slate-400 font-medium">Apostas</th>
                    <th className="text-right p-3 text-slate-400 font-medium">WR</th>
                    <th className="text-right p-3 text-slate-400 font-medium">ROI</th>
                  </tr>
                </thead>
                <tbody>
                  {by_sport.map((sport) => (
                    <tr key={sport.sport} className="border-b border-slate-800 hover:bg-slate-800/50">
                      <td className="p-3 text-2xl">{getMedal(sport.rank)}</td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{sport.icon}</span>
                          <span className="text-white font-medium">{sport.name}</span>
                        </div>
                      </td>
                      <td className="p-3 text-right text-slate-300">{sport.total_bets}</td>
                      <td className="p-3 text-right">
                        <span className={getPerformanceColor(sport.win_rate - 52.38)}>
                          {sport.win_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <span className={`font-bold ${getPerformanceColor(sport.roi)}`}>
                          {sport.roi > 0 ? "+" : ""}{sport.roi.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Performance by Market */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-white">
              📊 Performance por Mercado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {by_market.map((market) => (
                <div
                  key={market.market}
                  className={`p-4 rounded-lg border-2 ${getBorderColor(market.roi)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">{market.name}</h4>
                    <Badge
                      variant={market.roi > 0 ? "default" : "destructive"}
                      className={market.roi > 0 ? "bg-green-600" : "bg-red-600"}
                    >
                      {market.roi > 0 ? "+" : ""}{market.roi.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">
                      {market.total_bets} apostas • {market.wins}W-{market.total_bets - market.wins}L
                    </span>
                    <span className={getPerformanceColor(market.win_rate - 52.38)}>
                      WR: {market.win_rate.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <div className="mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-white">
              💡 Insights Automáticos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {insights.map((insight, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${getInsightColor(insight.type)}`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{getInsightIcon(insight.type)}</span>
                    <div>
                      <h4 className="font-bold text-white mb-1">{insight.title}</h4>
                      <p className="text-sm text-slate-300">{insight.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
