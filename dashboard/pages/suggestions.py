"""Bet suggestions page."""
import streamlit as st
from database.db import get_db_session
from database.models import Bet
from betting.tracker import BetTracker
from utils.helpers import format_currency, format_percentage, format_odds


def show():
    """Display bet suggestions page."""
    st.header("💡 Apostas Sugeridas")
    st.write("Revise e confirme as apostas sugeridas pelo sistema")
    
    tracker = BetTracker()
    
    # Get pending suggestions and convert to dictionaries
    db = get_db_session()
    try:
        suggestions = db.query(Bet).filter(
            Bet.confirmed == False,
            Bet.status == "pending"
        ).all()
        
        # Convert to dictionaries immediately while session is active
        suggestion_data = []
        for bet in suggestions:
            match = bet.match
            if not match:
                continue
                
            suggestion_data.append({
                'bet_id': bet.id,
                'team1': match.team1,
                'team2': match.team2,
                'game': match.game,
                'tournament': match.tournament,
                'start_time': match.start_time,
                'best_of': match.best_of,
                'market_type': bet.market_type,
                'selection': bet.selection,
                'bookmaker': bet.bookmaker,
                'odds': bet.odds,
                'stake': bet.stake,
                'confidence': bet.confidence,
                'edge': bet.edge,
            })
    finally:
        db.close()
    
    if not suggestion_data:
        st.info("✅ Sem novas sugestões de apostas no momento")
        return
    
    st.success(f"**{len(suggestion_data)} nova(s) sugestão(ões)**")
    
    # Display each suggestion
    for data in suggestion_data:
        with st.expander(f"**{data['team1']} vs {data['team2']}** - {data['game']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Partida:** {data['team1']} vs {data['team2']}")
                st.write(f"**Jogo:** {data['game']}")
                st.write(f"**Torneio:** {data['tournament'] or 'N/A'}")
                if data['start_time']:
                    st.write(f"**Início:** {data['start_time'].strftime('%d/%m/%Y %H:%M')}")
                st.write(f"**Formato:** BO{data['best_of']}")
                
                st.markdown("---")
                
                st.write(f"**Mercado:** {data['market_type']}")
                st.write(f"**Seleção:** {data['selection']}")
                st.write(f"**Casa:** {data['bookmaker']}")
                st.write(f"**Odds:** {format_odds(data['odds'])}")
                st.write(f"**Stake:** {format_currency(data['stake'])}")
            
            with col2:
                st.metric("Confidence", format_percentage(data['confidence']))
                st.metric("Edge", format_percentage(data['edge']))
                st.metric("Retorno Esperado", format_currency((data['odds'] - 1) * data['stake']))
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(f"✅ Confirmar", key=f"confirm_{data['bet_id']}"):
                    tracker.confirm_bet(data['bet_id'])
                    st.success("Aposta confirmada!")
                    st.rerun()
            
            with col_b:
                if st.button(f"❌ Ignorar", key=f"cancel_{data['bet_id']}"):
                    tracker.cancel_bet(data['bet_id'])
                    st.warning("Aposta ignorada")
                    st.rerun()
