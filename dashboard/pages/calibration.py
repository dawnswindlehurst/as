"""Model calibration page."""
import streamlit as st
import plotly.graph_objects as go
from validation.calibration import CalibrationValidator
from validation.clv import CLVAnalyzer
from config.constants import CONFIDENCE_RANGES
from utils.helpers import format_percentage


def show():
    """Display calibration page."""
    st.header("📊 Calibração dos Modelos")
    st.write("Análise de calibração e precisão dos modelos preditivos")
    
    calibration_validator = CalibrationValidator()
    clv_analyzer = CLVAnalyzer()
    
    # Calibration validation
    st.subheader("🎯 Validação de Calibração")
    
    validation = calibration_validator.validate_calibration()
    
    if validation:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Apostas", validation.get("total_bets", 0))
        
        with col2:
            brier = validation.get("brier_score", 0)
            st.metric("Brier Score", f"{brier:.4f}")
            st.caption("Menor é melhor (< 0.1 é bom)")
        
        with col3:
            log_loss = validation.get("log_loss", 0)
            st.metric("Log Loss", f"{log_loss:.4f}")
            st.caption("Menor é melhor")
        
        # Calibration curve
        if "calibration_curve" in validation:
            st.markdown("---")
            st.subheader("📈 Curva de Calibração")
            
            curve = validation["calibration_curve"]
            predicted = curve.get("predicted", [])
            actual = curve.get("actual", [])
            
            if predicted and actual:
                fig = go.Figure()
                
                # Perfect calibration line
                fig.add_trace(go.Scatter(
                    x=[0, 1],
                    y=[0, 1],
                    mode='lines',
                    name='Calibração Perfeita',
                    line=dict(dash='dash', color='gray'),
                ))
                
                # Actual calibration
                fig.add_trace(go.Scatter(
                    x=predicted,
                    y=actual,
                    mode='lines+markers',
                    name='Calibração Real',
                    line=dict(color='blue'),
                    marker=dict(size=8),
                ))
                
                fig.update_layout(
                    title="Curva de Calibração",
                    xaxis_title="Probabilidade Prevista",
                    yaxis_title="Frequência Real de Vitórias",
                    hovermode='x',
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("""
                **Como interpretar:**
                - Pontos **próximos à linha diagonal** = boa calibração
                - Pontos **acima da linha** = modelo subestima probabilidades
                - Pontos **abaixo da linha** = modelo superestima probabilidades
                """)
    else:
        st.info("Sem dados suficientes para validação de calibração")
    
    st.markdown("---")
    
    # CLV Analysis
    st.subheader("📈 Análise de CLV (Closing Line Value)")
    
    clv_stats = clv_analyzer.calculate_clv_stats()
    
    if clv_stats.get("total_bets", 0) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total com CLV", clv_stats.get("total_bets", 0))
        
        with col2:
            avg_clv = clv_stats.get("avg_clv_percent", 0)
            st.metric("CLV Médio", f"{avg_clv:.2f}%")
            st.caption("Positivo indica edge real")
        
        with col3:
            positive_rate = clv_stats.get("positive_clv_rate", 0)
            st.metric("Taxa CLV Positivo", format_percentage(positive_rate))
        
        # CLV by confidence
        st.markdown("---")
        st.subheader("🎯 CLV por Confidence Range")
        
        clv_by_conf = clv_analyzer.analyze_clv_by_confidence(CONFIDENCE_RANGES)
        
        if clv_by_conf:
            clv_data = []
            for range_name, stats in clv_by_conf.items():
                clv_data.append({
                    "Range": range_name,
                    "Apostas": stats.get("count", 0),
                    "CLV Médio": f"{stats.get('avg_clv_percent', 0):.2f}%",
                    "Taxa CLV+": format_percentage(stats.get("positive_clv_rate", 0)),
                })
            
            st.dataframe(clv_data, use_container_width=True, hide_index=True)
        
        # CLV correlation with results
        st.markdown("---")
        st.subheader("🔗 Correlação CLV x Resultados")
        
        correlation = clv_analyzer.get_clv_correlation_with_results()
        
        if correlation:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**CLV Positivo**")
                pos = correlation.get("positive_clv", {})
                st.metric("Win Rate", format_percentage(pos.get("win_rate", 0)))
                st.metric("Total Apostas", pos.get("total", 0))
            
            with col2:
                st.write("**CLV Negativo**")
                neg = correlation.get("negative_clv", {})
                st.metric("Win Rate", format_percentage(neg.get("win_rate", 0)))
                st.metric("Total Apostas", neg.get("total", 0))
            
            st.success("""
            **CLV positivo correlacionado com melhor win rate** 
            indica que o modelo tem edge real no mercado.
            """)
    else:
        st.info("Sem dados de CLV disponíveis ainda")
