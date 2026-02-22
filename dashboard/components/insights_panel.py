"""Insights panel component for displaying automated insights."""
import streamlit as st
from typing import List
from analysis.insights import Insight


def insights_panel(
    insights: List[Insight],
    title: str = "💡 Insights e Recomendações",
    max_insights: int = None
):
    """Display insights panel with recommendations.
    
    Args:
        insights: List of Insight objects
        title: Panel title
        max_insights: Maximum number of insights to show (None = all)
    """
    st.subheader(title)
    
    if not insights:
        st.info("Nenhum insight disponível no momento")
        return
    
    # Limit if requested
    display_insights = insights[:max_insights] if max_insights else insights
    
    # Group by type
    success_insights = [i for i in display_insights if i.type == 'success']
    info_insights = [i for i in display_insights if i.type == 'info']
    warning_insights = [i for i in display_insights if i.type == 'warning']
    danger_insights = [i for i in display_insights if i.type == 'danger']
    
    # Display by priority/type
    for insight in danger_insights:
        _display_insight(insight, '🔴')
    
    for insight in warning_insights:
        _display_insight(insight, '⚠️')
    
    for insight in success_insights:
        _display_insight(insight, '✅')
    
    for insight in info_insights:
        _display_insight(insight, 'ℹ️')


def _display_insight(insight: Insight, icon: str):
    """Display a single insight.
    
    Args:
        insight: Insight object
        icon: Emoji icon
    """
    # Determine color based on type
    if insight.type == 'success':
        color = '#00C853'
        border_color = '#00C853'
    elif insight.type == 'info':
        color = '#2196F3'
        border_color = '#2196F3'
    elif insight.type == 'warning':
        color = '#FFC107'
        border_color = '#FFC107'
    else:  # danger
        color = '#F44336'
        border_color = '#F44336'
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}10 0%, {color}05 100%);
        border-left: 4px solid {border_color};
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.75rem 0;
    ">
        <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.5rem;">
            {icon} {insight.title}
        </div>
        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">
            {insight.description}
        </div>
        <div style="font-size: 0.875rem; color: #333; font-weight: 500;">
            💡 {insight.action}
        </div>
    </div>
    """, unsafe_allow_html=True)


def insights_summary(insights: List[Insight]):
    """Display a summary of insights by type.
    
    Args:
        insights: List of Insight objects
    """
    if not insights:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    success_count = len([i for i in insights if i.type == 'success'])
    info_count = len([i for i in insights if i.type == 'info'])
    warning_count = len([i for i in insights if i.type == 'warning'])
    danger_count = len([i for i in insights if i.type == 'danger'])
    
    with col1:
        st.metric("✅ Sucessos", success_count)
    
    with col2:
        st.metric("ℹ️ Informativos", info_count)
    
    with col3:
        st.metric("⚠️ Avisos", warning_count)
    
    with col4:
        st.metric("🔴 Críticos", danger_count)


def top_insights_cards(insights: List[Insight], n: int = 3):
    """Display top N insights as cards.
    
    Args:
        insights: List of Insight objects
        n: Number of top insights to show
    """
    if not insights:
        return
    
    st.subheader(f"🔝 Top {n} Insights")
    
    top = insights[:n]
    
    for i, insight in enumerate(top, 1):
        with st.expander(f"{i}. {insight.title}", expanded=(i == 1)):
            st.markdown(f"**Descrição:** {insight.description}")
            st.markdown(f"**Ação Recomendada:** {insight.action}")
            st.markdown(f"**Prioridade:** {'🔴 Alta' if insight.priority == 1 else '🟡 Média' if insight.priority == 2 else '🟢 Baixa'}")


def insights_by_category(insights: List[Insight]):
    """Display insights organized by category in tabs.
    
    Args:
        insights: List of Insight objects
    """
    if not insights:
        st.info("Nenhum insight disponível")
        return
    
    # Categorize insights based on title keywords
    performance = []
    risk = []
    calibration = []
    clv = []
    other = []
    
    for insight in insights:
        title_lower = insight.title.lower()
        if any(word in title_lower for word in ['roi', 'win rate', 'acerto', 'lucro', 'performance']):
            performance.append(insight)
        elif any(word in title_lower for word in ['sharpe', 'drawdown', 'risco', 'volatilidade']):
            risk.append(insight)
        elif any(word in title_lower for word in ['calibração', 'brier', 'margem']):
            calibration.append(insight)
        elif any(word in title_lower for word in ['clv', 'edge']):
            clv.append(insight)
        else:
            other.append(insight)
    
    # Create tabs
    tab_names = []
    tab_contents = []
    
    if performance:
        tab_names.append("📈 Performance")
        tab_contents.append(performance)
    if risk:
        tab_names.append("⚠️ Risco")
        tab_contents.append(risk)
    if calibration:
        tab_names.append("🎯 Calibração")
        tab_contents.append(calibration)
    if clv:
        tab_names.append("💰 CLV")
        tab_contents.append(clv)
    if other:
        tab_names.append("📊 Outros")
        tab_contents.append(other)
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        for tab, content in zip(tabs, tab_contents):
            with tab:
                for insight in content:
                    _display_insight(insight, '')


def actionable_insights(insights: List[Insight], priority: int = 1):
    """Display only actionable insights (high priority).
    
    Args:
        insights: List of Insight objects
        priority: Maximum priority to show (1=high, 2=medium, 3=low)
    """
    actionable = [i for i in insights if i.priority <= priority]
    
    if not actionable:
        st.success("✅ Nenhuma ação urgente necessária!")
        return
    
    st.warning(f"⚡ {len(actionable)} ação(ões) recomendada(s)")
    
    for i, insight in enumerate(actionable, 1):
        with st.container():
            st.markdown(f"**{i}. {insight.title}**")
            st.markdown(f"🎯 {insight.action}")
            st.markdown("---")
