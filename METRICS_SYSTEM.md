# Sistema Completo de Métricas - Paper Trading

## 📊 Visão Geral

Este sistema fornece uma análise completa e automatizada para validação de estratégias de apostas durante o período de Paper Trading. Com métricas avançadas, visualizações interativas e insights automáticos, permite avaliar de forma precisa se o sistema está pronto para operação real.

## 🎯 Configuração do Paper Trading

```python
PAPER_TRADING_CONFIG = {
    'stake': 10.00,  # R$ 10,00 por aposta
    'currency': 'BRL',
    'duration': '1_week_to_1_month',
    'initial_bankroll': 1000.00,  # R$ 1.000,00 inicial
    'min_edge': 0.03,  # 3% edge mínimo
    'min_confidence': 0.55,  # 55% confidence mínimo
}
```

## 📈 Módulos de Métricas

### 1. BasicMetrics (`analysis/metrics/basic.py`)
Métricas fundamentais de performance:
- **win_rate**: Taxa de acerto (%)
- **roi**: Retorno sobre investimento (%)
- **profit**: Lucro líquido em R$
- **yield_per_bet**: Lucro médio por aposta
- **total_wagered**: Total apostado
- **total_bets**: Quantidade de apostas
- **average_odds**: Odds média
- **average_stake**: Stake médio

### 2. RiskMetrics (`analysis/metrics/risk.py`)
Análise de risco ajustado ao retorno:
- **sharpe_ratio**: Retorno ajustado ao risco
- **sortino_ratio**: Sharpe considerando apenas downside
- **max_drawdown**: Maior queda do pico ao vale (%)
- **max_drawdown_duration**: Dias no drawdown máximo
- **recovery_factor**: Lucro Total / Max Drawdown
- **calmar_ratio**: ROI Anualizado / Max Drawdown
- **volatility**: Desvio padrão dos retornos (%)
- **var_95**: Value at Risk (95% confiança)
- **cvar_95**: Conditional VaR (média piores perdas)

### 3. CalibrationMetrics (`analysis/metrics/calibration.py`)
Qualidade das probabilidades do modelo:
- **brier_score**: Erro quadrático médio das probabilidades
- **log_loss**: Cross-entropy loss
- **calibration_error**: Diferença entre previsto e real
- **overround_beat_rate**: % batendo margem da casa
- **calibration_bins**: Dados para curva de calibração

### 4. CLVMetrics (`analysis/metrics/clv.py`)
Closing Line Value - validação de edge:
- **clv_average**: CLV médio das apostas
- **clv_positive_rate**: % de apostas com CLV+
- **clv_by_sport**: CLV médio por esporte
- **clv_by_market**: CLV médio por mercado
- **clv_correlation**: Correlação entre CLV e resultado
- **edge_realized**: Edge teórico vs realizado

### 5. StreakMetrics (`analysis/metrics/streaks.py`)
Consistência e padrões:
- **current_streak**: Streak atual (W ou L)
- **longest_win_streak**: Maior sequência de vitórias
- **longest_lose_streak**: Maior sequência de derrotas
- **average_win_streak**: Tamanho médio win streaks
- **average_lose_streak**: Tamanho médio lose streaks
- **win_after_loss**: Win rate após derrota
- **win_after_win**: Win rate após vitória
- **consecutive_profitable_days**: Dias seguidos no lucro

### 6. BankrollMetrics (`analysis/metrics/bankroll.py`)
Gestão de bankroll:
- **current_bankroll**: Saldo atual simulado
- **bankroll_growth**: Crescimento % do bankroll
- **units_won**: Lucro em unidades
- **kelly_suggested**: Stake sugerido pelo Kelly
- **break_even_winrate**: Win rate necessário para empatar
- **expected_value_per_bet**: EV médio por aposta
- **roi_if_flat**: ROI se usasse flat betting
- **equity_curve**: Evolução do bankroll

## 🔧 Uso do Sistema

### Cálculo de Métricas

```python
from analysis.metrics.aggregator import MetricsAggregator

# Inicializar com configuração padrão
aggregator = MetricsAggregator(
    initial_bankroll=1000.00,
    risk_free_rate=0.0
)

# Calcular todas as métricas
all_metrics = aggregator.calculate_all()

# Métricas por esporte
metrics_by_sport = aggregator.calculate_by_sport(['CS2', 'Dota2', 'LoL'])

# Métricas por mercado
metrics_by_market = aggregator.calculate_by_market(['match_winner', 'handicap'])

# Métricas por faixa de confidence
from config.metrics_config import CONFIDENCE_RANGES
metrics_by_conf = aggregator.calculate_by_confidence_range(CONFIDENCE_RANGES)
```

### Geração de Insights

```python
from analysis.insights import InsightGenerator

# Gerar insights automáticos
insight_gen = InsightGenerator(all_metrics)
insights = insight_gen.generate_all_insights()

# Top 5 insights prioritários
top_insights = insight_gen.get_top_insights(n=5)

# Insights por tipo
success_insights = insight_gen.get_insights_by_type('success')
warning_insights = insight_gen.get_insights_by_type('warning')
```

## 📊 Dashboard Pages

### 1. Dashboard de Métricas (`metrics_dashboard.py`)
**Acesso:** Menu lateral → Métricas → 📊 Dashboard de Métricas

Página principal com:
- KPIs principais (6 cards)
- Métricas de risco (4 cards)
- Métricas de calibração (4 cards)
- Tabelas por esporte, mercado, confidence e odds
- Gráficos de equity e calibração
- Painel de insights automáticos

### 2. Relatório de Validação (`validation_report.py`)
**Acesso:** Menu lateral → Métricas → 📋 Relatório de Validação

Relatório completo incluindo:
- Resumo executivo com recomendação final
- Top 10 mercados mais lucrativos
- Bottom 5 mercados a evitar
- Análise detalhada por dimensões (tabs)
- Conclusões e recomendações automáticas
- Opções de exportação (PDF/Excel)

### 3. Análise de Mercados (`market_analysis.py`)
**Acesso:** Menu lateral → Métricas → 🎯 Análise de Mercados

Análise profunda de mercados:
- Visão geral com cards resumidos
- Comparação lado a lado
- Deep dive em mercado específico
- Heatmap Esporte × Mercado
- Gráficos de equity por mercado

## 🎨 Componentes de Visualização

### Metric Cards
```python
from dashboard.components.metric_card import metric_card, metrics_row

# Card individual
metric_card(
    title='ROI',
    value=15.5,
    delta='+5%',
    icon='💰'
)

# Múltiplos cards em linha
metrics_row([
    {'title': 'Win Rate', 'value': '58.3%', 'icon': '📈'},
    {'title': 'Sharpe', 'value': 1.85, 'icon': '📊'},
])
```

### Tabelas
```python
from dashboard.components.metrics_table import metrics_table

metrics_table(
    data=metrics_by_sport,
    title='Performance por Esporte',
    sort_by='roi',
    ascending=False
)
```

### Gráficos
```python
from dashboard.components.equity_chart import equity_chart
from dashboard.components.calibration_chart import calibration_curve

# Equity curve
equity_chart(equity_data, initial_bankroll=1000.0)

# Calibration curve
calibration_curve(calibration_bins)
```

### Heatmaps
```python
from dashboard.components.heatmap import performance_heatmap

performance_heatmap(
    data=heatmap_data,
    title='Heatmap de Performance',
    metric='roi'
)
```

### Insights Panel
```python
from dashboard.components.insights_panel import insights_panel

insights_panel(
    insights=insights,
    title='💡 Insights e Recomendações',
    max_insights=10
)
```

## 📐 Dimensões de Análise

O sistema permite segmentar métricas por:

- **Esporte**: CS2, Dota2, Valorant, LoL, Tennis, Football
- **Mercado**: 20+ tipos incluindo ML, Handicap, Totals, Specials
- **Confidence Range**: 55-60%, 60-65%, 65-70%, 70-75%, 75%+
- **Odds Range**: 1.20-1.50, 1.50-1.80, 1.80-2.20, 2.20-3.00, 3.00+
- **Modelo**: elo, glicko, logistic, xgboost, poisson, ensemble
- **Outras**: Weekday, Hour, Tier, Region, Format, Favorite/Underdog

## 🎯 Thresholds e Interpretação

### Performance (ROI)
- **Excelente**: ≥ 15%
- **Bom**: ≥ 8%
- **Pobre**: < -5%

### Win Rate
- **Excelente**: ≥ 60%
- **Bom**: ≥ 55%
- **Pobre**: < 45%

### Sharpe Ratio
- **Excelente**: ≥ 2.0
- **Bom**: ≥ 1.0
- **Pobre**: < 0.0

### Drawdown
- **Atenção**: > 20%
- **Perigoso**: > 30%

### Brier Score
- **Excelente**: < 0.15
- **Bom**: < 0.20
- **Pobre**: > 0.25

### CLV
- **Excelente**: > +0.05
- **Bom**: > +0.02
- **Pobre**: < -0.02

## 🚀 Quick Start

1. **Certifique-se de ter apostas no banco de dados**
   ```python
   # Apostas devem ter:
   # - confirmed = True
   # - status in ['won', 'lost', 'pending']
   # - Campos preenchidos: odds, stake, profit, etc.
   ```

2. **Acesse o Dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

3. **Navegue para Métricas**
   - Menu lateral → Métricas → 📊 Dashboard de Métricas

4. **Explore as Análises**
   - Dashboard principal para overview
   - Relatório de Validação para decisão final
   - Análise de Mercados para deep dives

## 📝 Checklist de Validação

Antes de aprovar para operação real, verificar:

- [ ] ROI consistentemente positivo (> 8%)
- [ ] Sharpe Ratio > 1.0
- [ ] Win Rate alinhada com odds médias
- [ ] Max Drawdown < 20%
- [ ] CLV positivo (> 55% das apostas)
- [ ] Brier Score < 0.25 (modelo calibrado)
- [ ] Amostra mínima de 100 apostas
- [ ] Performance consistente em múltiplos mercados
- [ ] Sem dependência de um único mercado
- [ ] Insights não mostram problemas críticos

## 🔄 Workflow Recomendado

1. **Semana 1**: Coleta inicial de dados
   - Mínimo 30 apostas
   - Verificar funcionamento dos modelos
   - Ajustar critérios se necessário

2. **Semana 2-3**: Validação intermediária
   - Analisar métricas no Dashboard
   - Identificar mercados problemáticos
   - Refinar estratégias

3. **Semana 4**: Decisão final
   - Gerar Relatório de Validação
   - Revisar todos os insights
   - Decidir: Aprovar, Ajustar ou Rejeitar

## 🛠️ Troubleshooting

### "Nenhum dado disponível"
- Verificar se existem apostas com `confirmed=True`
- Verificar se apostas estão settled (`status` = 'won'/'lost')

### "Dados insuficientes"
- Aumentar período de coleta
- Reduzir filtros de segmentação
- Verificar campo `market_type` nas apostas

### Métricas estranhas/inconsistentes
- Verificar integridade dos dados (profit, stake, odds)
- Confirmar que `settled_at` está preenchido
- Validar cálculos de CLV (precisa de `closing_odds`)

## 📚 Referências

- **Sharpe Ratio**: Medida clássica de retorno ajustado ao risco
- **Brier Score**: Métrica padrão para calibração probabilística
- **CLV (Closing Line Value)**: Indicador-chave de edge em apostas
- **Kelly Criterion**: Fórmula ótima para sizing de stakes

## 🤝 Contribuindo

Para adicionar novas métricas:

1. Criar classe em `analysis/metrics/`
2. Herdar de `MetricsCalculator`
3. Implementar método `calculate()`
4. Adicionar ao `MetricsAggregator`
5. Atualizar componentes de visualização
6. Documentar no README

---

**Desenvolvido para Capivara Bet Esports 2.0**
