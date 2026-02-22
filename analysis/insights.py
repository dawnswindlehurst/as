"""Automatic insights generation from metrics."""
from typing import Dict, List
from dataclasses import dataclass
from config.metrics_config import METRICS_THRESHOLDS, METRIC_COLORS


@dataclass
class Insight:
    """Represents a single insight."""
    type: str  # 'success', 'info', 'warning', 'danger'
    title: str
    description: str
    action: str
    priority: int = 1  # 1=high, 2=medium, 3=low


class InsightGenerator:
    """Generate automated insights from metrics."""
    
    def __init__(self, metrics: Dict, thresholds: Dict = None):
        """Initialize insight generator.
        
        Args:
            metrics: Complete metrics dictionary from MetricsAggregator
            thresholds: Custom thresholds (uses defaults if None)
        """
        self.metrics = metrics
        self.thresholds = thresholds or METRICS_THRESHOLDS
    
    def generate_all_insights(self) -> List[Insight]:
        """Generate all insights from metrics.
        
        Returns:
            List of Insight objects, sorted by priority
        """
        insights = []
        
        # Performance insights
        insights.extend(self._generate_performance_insights())
        
        # Risk insights
        insights.extend(self._generate_risk_insights())
        
        # Calibration insights
        insights.extend(self._generate_calibration_insights())
        
        # CLV insights
        insights.extend(self._generate_clv_insights())
        
        # Streak insights
        insights.extend(self._generate_streak_insights())
        
        # Bankroll insights
        insights.extend(self._generate_bankroll_insights())
        
        # Sort by priority
        return sorted(insights, key=lambda x: x.priority)
    
    def _generate_performance_insights(self) -> List[Insight]:
        """Generate insights from basic performance metrics."""
        insights = []
        basic = self.metrics.get('basic', {})
        
        if not basic:
            return insights
        
        roi = basic.get('roi', 0)
        win_rate = basic.get('win_rate', 0)
        total_bets = basic.get('total_bets', 0)
        
        # ROI insights
        if roi >= self.thresholds['excellent_roi']:
            insights.append(Insight(
                type='success',
                title='🎯 ROI Excelente',
                description=f'ROI de {roi:.1f}% está acima do limiar de excelência ({self.thresholds["excellent_roi"]:.1f}%)',
                action='Continuar estratégia atual - modelo está performando muito bem',
                priority=1
            ))
        elif roi >= self.thresholds['good_roi']:
            insights.append(Insight(
                type='info',
                title='✅ ROI Positivo',
                description=f'ROI de {roi:.1f}% está no intervalo bom',
                action='Performance satisfatória - monitorar consistência',
                priority=2
            ))
        elif roi <= self.thresholds['poor_roi']:
            insights.append(Insight(
                type='danger',
                title='⚠️ ROI Negativo',
                description=f'ROI de {roi:.1f}% está abaixo do aceitável',
                action='URGENTE: Revisar estratégia, modelos e seleção de apostas',
                priority=1
            ))
        
        # Win rate insights
        if win_rate >= self.thresholds['excellent_winrate']:
            insights.append(Insight(
                type='success',
                title='🏆 Taxa de Acerto Alta',
                description=f'Win rate de {win_rate:.1f}% é excelente',
                action='Modelo bem calibrado - manter critérios de seleção',
                priority=2
            ))
        elif win_rate <= self.thresholds['poor_winrate']:
            insights.append(Insight(
                type='warning',
                title='📉 Taxa de Acerto Baixa',
                description=f'Win rate de {win_rate:.1f}% está abaixo do esperado',
                action='Revisar calibração do modelo e critérios de confidence',
                priority=1
            ))
        
        # Sample size insight
        if total_bets < 30:
            insights.append(Insight(
                type='info',
                title='📊 Amostra Pequena',
                description=f'Apenas {total_bets} apostas - resultados podem ter alta variância',
                action='Continuar coletando dados antes de conclusões definitivas',
                priority=3
            ))
        
        return insights
    
    def _generate_risk_insights(self) -> List[Insight]:
        """Generate insights from risk metrics."""
        insights = []
        risk = self.metrics.get('risk', {})
        
        if not risk:
            return insights
        
        sharpe = risk.get('sharpe_ratio', 0)
        max_dd = risk.get('max_drawdown', 0)
        volatility = risk.get('volatility', 0)
        
        # Sharpe ratio insights
        if sharpe >= self.thresholds['excellent_sharpe']:
            insights.append(Insight(
                type='success',
                title='📈 Sharpe Ratio Excelente',
                description=f'Sharpe de {sharpe:.2f} indica retorno ajustado ao risco muito bom',
                action='Risco bem gerenciado - continuar abordagem',
                priority=2
            ))
        elif sharpe <= self.thresholds['poor_sharpe']:
            insights.append(Insight(
                type='warning',
                title='⚠️ Sharpe Ratio Baixo',
                description=f'Sharpe de {sharpe:.2f} indica retorno não justifica o risco',
                action='Considerar redução de stake ou filtros mais rigorosos',
                priority=1
            ))
        
        # Drawdown insights
        if abs(max_dd) >= self.thresholds['danger_drawdown']:
            insights.append(Insight(
                type='danger',
                title='🔴 Drawdown Perigoso',
                description=f'Max drawdown de {abs(max_dd):.1f}% é muito alto',
                action='CRÍTICO: Reduzir exposição imediatamente ou pausar operações',
                priority=1
            ))
        elif abs(max_dd) >= self.thresholds['warning_drawdown']:
            insights.append(Insight(
                type='warning',
                title='⚠️ Drawdown Elevado',
                description=f'Max drawdown de {abs(max_dd):.1f}% merece atenção',
                action='Revisar bankroll management e considerar reduzir stakes',
                priority=2
            ))
        
        # Volatility insights
        if volatility >= self.thresholds['high_volatility']:
            insights.append(Insight(
                type='info',
                title='📊 Alta Volatilidade',
                description=f'Volatilidade de {volatility:.1f}% indica resultados inconsistentes',
                action='Considerar diversificar entre mais mercados ou reduzir stakes',
                priority=2
            ))
        
        return insights
    
    def _generate_calibration_insights(self) -> List[Insight]:
        """Generate insights from calibration metrics."""
        insights = []
        calibration = self.metrics.get('calibration', {})
        
        if not calibration:
            return insights
        
        brier = calibration.get('brier_score', 0)
        log_loss = calibration.get('log_loss', 0)
        overround_beat = calibration.get('overround_beat_rate', 0)
        
        # Brier score insights
        if brier <= self.thresholds['excellent_brier']:
            insights.append(Insight(
                type='success',
                title='✨ Calibração Excelente',
                description=f'Brier score de {brier:.3f} indica modelo muito bem calibrado',
                action='Probabilidades precisas - confiar nas estimativas',
                priority=2
            ))
        elif brier >= self.thresholds['poor_brier']:
            insights.append(Insight(
                type='warning',
                title='⚠️ Modelo Mal Calibrado',
                description=f'Brier score de {brier:.3f} indica problemas de calibração',
                action='Revisar modelos preditivos e recalibrar probabilidades',
                priority=1
            ))
        
        # Overround beat rate
        if overround_beat >= 60:
            insights.append(Insight(
                type='success',
                title='🎯 Batendo Margem da Casa',
                description=f'{overround_beat:.0f}% das apostas com edge positivo',
                action='Identificação de value funcionando bem',
                priority=2
            ))
        elif overround_beat <= 40:
            insights.append(Insight(
                type='warning',
                title='📉 Dificuldade em Bater Margem',
                description=f'Apenas {overround_beat:.0f}% com edge positivo',
                action='Revisar critérios de edge mínimo ou mercados escolhidos',
                priority=2
            ))
        
        return insights
    
    def _generate_clv_insights(self) -> List[Insight]:
        """Generate insights from CLV metrics."""
        insights = []
        clv = self.metrics.get('clv', {})
        
        if not clv:
            return insights
        
        clv_avg = clv.get('clv_average', 0)
        clv_positive_rate = clv.get('clv_positive_rate', 0)
        clv_correlation = clv.get('clv_correlation', 0)
        
        # Average CLV insights
        if clv_avg >= self.thresholds['excellent_clv']:
            insights.append(Insight(
                type='success',
                title='⭐ CLV Consistentemente Positivo',
                description=f'CLV médio de {clv_avg:.3f} é excelente',
                action='Edge real comprovado - continuar estratégia',
                priority=1
            ))
        elif clv_avg <= self.thresholds['poor_clv']:
            insights.append(Insight(
                type='danger',
                title='🔴 CLV Negativo',
                description=f'CLV médio de {clv_avg:.3f} indica apostas ruins',
                action='CRÍTICO: Timing ruim ou modelos imprecisos - revisar',
                priority=1
            ))
        
        # CLV positive rate
        if clv_positive_rate >= self.thresholds['excellent_clv_rate']:
            insights.append(Insight(
                type='success',
                title='✅ Alta Taxa de CLV+',
                description=f'{clv_positive_rate:.0f}% das apostas com CLV positivo',
                action='Timing de entrada muito bom - manter',
                priority=2
            ))
        elif clv_positive_rate <= self.thresholds['poor_clv_rate']:
            insights.append(Insight(
                type='warning',
                title='⚠️ Baixa Taxa de CLV+',
                description=f'Apenas {clv_positive_rate:.0f}% com CLV positivo',
                action='Melhorar timing ou revisar seleção de mercados',
                priority=2
            ))
        
        # CLV correlation
        if clv_correlation > 0.3:
            insights.append(Insight(
                type='success',
                title='📊 CLV Correlaciona com Vitórias',
                description=f'Correlação de {clv_correlation:.2f} entre CLV e resultado',
                action='CLV é bom preditor - continuar focando nele',
                priority=3
            ))
        
        return insights
    
    def _generate_streak_insights(self) -> List[Insight]:
        """Generate insights from streak metrics."""
        insights = []
        streaks = self.metrics.get('streaks', {})
        
        if not streaks:
            return insights
        
        current = streaks.get('current_streak', {})
        longest_lose = streaks.get('longest_lose_streak', 0)
        win_after_loss = streaks.get('win_after_loss', 0)
        
        # Current losing streak warning
        if current.get('type') == 'loss' and current.get('count', 0) >= 5:
            insights.append(Insight(
                type='warning',
                title='⚠️ Sequência de Derrotas',
                description=f'{current["count"]} derrotas consecutivas',
                action='Evitar decisões emocionais - manter disciplina',
                priority=1
            ))
        
        # Longest losing streak
        if longest_lose >= 10:
            insights.append(Insight(
                type='info',
                title='📊 Sequência Longa de Derrotas',
                description=f'Maior sequência foi de {longest_lose} derrotas',
                action='Normal em apostas - importante ter bankroll para aguentar',
                priority=3
            ))
        
        # Recovery after losses
        if win_after_loss >= 60:
            insights.append(Insight(
                type='success',
                title='💪 Boa Recuperação',
                description=f'{win_after_loss:.0f}% de vitórias após derrotas',
                action='Sem tilt aparente - disciplina mantida',
                priority=3
            ))
        
        return insights
    
    def _generate_bankroll_insights(self) -> List[Insight]:
        """Generate insights from bankroll metrics."""
        insights = []
        bankroll = self.metrics.get('bankroll', {})
        
        if not bankroll:
            return insights
        
        growth = bankroll.get('bankroll_growth', 0)
        kelly = bankroll.get('kelly_suggested', 0)
        ev_per_bet = bankroll.get('expected_value_per_bet', 0)
        
        # Bankroll growth
        if growth >= 20:
            insights.append(Insight(
                type='success',
                title='📈 Crescimento Excelente',
                description=f'Bankroll cresceu {growth:.1f}%',
                action='Performance excepcional - documentar estratégia',
                priority=1
            ))
        elif growth <= -15:
            insights.append(Insight(
                type='danger',
                title='📉 Perda Significativa',
                description=f'Bankroll caiu {abs(growth):.1f}%',
                action='URGENTE: Pausar e reavaliar completamente',
                priority=1
            ))
        
        # Kelly criterion
        if kelly >= 5:
            insights.append(Insight(
                type='info',
                title='📊 Kelly Sugere Stakes Maiores',
                description=f'Kelly médio de {kelly:.1f}% do bankroll',
                action='Considerar aumentar stakes se confortável com risco',
                priority=3
            ))
        
        # Expected value
        if ev_per_bet > 0.5:
            insights.append(Insight(
                type='success',
                title='💰 EV Positivo Forte',
                description=f'EV médio de R$ {ev_per_bet:.2f} por aposta',
                action='Edge matemático comprovado - continuar',
                priority=2
            ))
        
        return insights
    
    def get_top_insights(self, n: int = 5) -> List[Insight]:
        """Get top N insights by priority.
        
        Args:
            n: Number of insights to return
            
        Returns:
            List of top insights
        """
        all_insights = self.generate_all_insights()
        return all_insights[:n]
    
    def get_insights_by_type(self, insight_type: str) -> List[Insight]:
        """Get insights filtered by type.
        
        Args:
            insight_type: 'success', 'info', 'warning', or 'danger'
            
        Returns:
            List of filtered insights
        """
        all_insights = self.generate_all_insights()
        return [i for i in all_insights if i.type == insight_type]
