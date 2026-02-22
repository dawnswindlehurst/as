"""Calibration curve chart component."""
import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict


def calibration_curve(
    calibration_bins: List[Dict],
    title: str = "🎯 Curva de Calibração",
    height: int = 400
):
    """Display calibration curve chart.
    
    Args:
        calibration_bins: List of bin dictionaries with predicted/actual values
        title: Chart title
        height: Chart height in pixels
    """
    if not calibration_bins:
        st.info("Dados de calibração não disponíveis")
        return
    
    # Extract data
    predicted = [bin['predicted'] for bin in calibration_bins]
    actual = [bin['actual'] for bin in calibration_bins]
    counts = [bin['count'] for bin in calibration_bins]
    
    # Create figure
    fig = go.Figure()
    
    # Add perfect calibration line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Calibração Perfeita',
        line=dict(color='gray', dash='dash', width=2)
    ))
    
    # Add actual calibration line
    fig.add_trace(go.Scatter(
        x=predicted,
        y=actual,
        mode='lines+markers',
        name='Calibração Real',
        line=dict(color='#1E88E5', width=3),
        marker=dict(
            size=[c/2 for c in counts],  # Size proportional to count
            color='#1E88E5',
            line=dict(color='white', width=1)
        ),
        text=[f"N={c}" for c in counts],
        hovertemplate='Previsto: %{x:.2f}<br>Real: %{y:.2f}<br>%{text}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Probabilidade Prevista',
        yaxis_title='Frequência Real',
        height=height,
        hovermode='closest',
        template='plotly_white',
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add interpretation
    with st.expander("ℹ️ Como Interpretar"):
        st.markdown("""
        **Curva de Calibração:**
        - A linha cinza tracejada representa calibração perfeita
        - Pontos próximos à linha indicam boa calibração
        - Pontos acima da linha: modelo está subestimando probabilidades
        - Pontos abaixo da linha: modelo está superestimando probabilidades
        - Tamanho dos pontos indica quantidade de apostas no intervalo
        """)


def reliability_diagram(
    calibration_bins: List[Dict],
    title: str = "📊 Diagrama de Confiabilidade",
    height: int = 400
):
    """Display reliability diagram with histogram.
    
    Args:
        calibration_bins: List of bin dictionaries
        title: Chart title
        height: Chart height in pixels
    """
    if not calibration_bins:
        st.info("Dados não disponíveis")
        return
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add bars for count
    fig.add_trace(go.Bar(
        x=[f"{bin['bin_start']:.2f}-{bin['bin_end']:.2f}" for bin in calibration_bins],
        y=[bin['count'] for bin in calibration_bins],
        name='Quantidade',
        marker_color='lightblue',
        yaxis='y2',
        opacity=0.6
    ))
    
    # Add line for calibration
    predicted = [(bin['bin_start'] + bin['bin_end']) / 2 for bin in calibration_bins]
    actual = [bin['actual'] for bin in calibration_bins]
    
    fig.add_trace(go.Scatter(
        x=[f"{bin['bin_start']:.2f}-{bin['bin_end']:.2f}" for bin in calibration_bins],
        y=actual,
        mode='lines+markers',
        name='Freq. Real',
        line=dict(color='#1E88E5', width=3),
        marker=dict(size=10),
        yaxis='y1'
    ))
    
    # Add predicted line
    fig.add_trace(go.Scatter(
        x=[f"{bin['bin_start']:.2f}-{bin['bin_end']:.2f}" for bin in calibration_bins],
        y=predicted,
        mode='lines+markers',
        name='Freq. Prevista',
        line=dict(color='#00C853', width=2, dash='dash'),
        marker=dict(size=8),
        yaxis='y1'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Intervalo de Confiança',
        yaxis_title='Frequência',
        yaxis2=dict(
            title='Quantidade de Apostas',
            overlaying='y',
            side='right'
        ),
        height=height,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def brier_score_decomposition(
    brier_score: float,
    calibration_loss: float = None,
    refinement_loss: float = None,
    title: str = "🎯 Decomposição do Brier Score",
    height: int = 300
):
    """Display Brier score decomposition.
    
    Args:
        brier_score: Overall Brier score
        calibration_loss: Calibration component
        refinement_loss: Refinement component
        title: Chart title
        height: Chart height in pixels
    """
    st.subheader(title)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Brier Score Total",
            f"{brier_score:.4f}",
            help="Menor é melhor (0 = perfeito)"
        )
    
    if calibration_loss is not None:
        with col2:
            st.metric(
                "Componente Calibração",
                f"{calibration_loss:.4f}",
                help="Quão bem calibradas estão as probabilidades"
            )
    
    if refinement_loss is not None:
        with col3:
            st.metric(
                "Componente Refinamento",
                f"{refinement_loss:.4f}",
                help="Quão bem o modelo discrimina entre resultados"
            )
    
    # Interpretation
    if brier_score < 0.15:
        st.success("✅ Excelente calibração do modelo")
    elif brier_score < 0.20:
        st.info("ℹ️ Boa calibração do modelo")
    elif brier_score < 0.25:
        st.warning("⚠️ Calibração aceitável, pode melhorar")
    else:
        st.error("❌ Calibração ruim, modelo precisa de ajustes")
