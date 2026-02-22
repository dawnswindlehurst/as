"""Calendar view component for tournaments."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go


def render_calendar_view(
    events: List[Dict[str, Any]],
    year: int,
    month: int,
    game_filter: Optional[str] = None
):
    """
    Render a calendar view of events for a specific month.
    
    Args:
        events: List of event dictionaries
        year: Year to display
        month: Month to display (1-12)
        game_filter: Optional game filter
    """
    # Filter events by game if specified
    if game_filter:
        events = [e for e in events if e.get('sport_name') == game_filter]
    
    # Filter events for the specified month
    month_events = []
    for event in events:
        start_time = event.get('start_time')
        if isinstance(start_time, str):
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                continue
        else:
            start_dt = start_time
        
        if start_dt and start_dt.year == year and start_dt.month == month:
            month_events.append({
                **event,
                'start_dt': start_dt
            })
    
    if not month_events:
        st.info(f"Nenhum evento em {month}/{year}")
        return
    
    # Group events by day
    days_events = {}
    for event in month_events:
        day = event['start_dt'].day
        if day not in days_events:
            days_events[day] = []
        days_events[day].append(event)
    
    # Display calendar
    month_name = datetime(year, month, 1).strftime('%B %Y')
    st.subheader(f"📅 {month_name}")
    
    # Create calendar grid (7 columns for days of week)
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year, 12, 31)
    
    # Day names header
    day_names = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    cols = st.columns(7)
    for i, day_name in enumerate(day_names):
        with cols[i]:
            st.markdown(f"**{day_name}**")
    
    st.markdown("---")
    
    # Calendar days
    current_day = first_day
    week_cols = st.columns(7)
    day_of_week = current_day.weekday()
    # Adjust for Sunday as first day
    day_of_week = (day_of_week + 1) % 7
    
    day_num = 1
    while current_day <= last_day:
        col_idx = day_of_week
        
        with week_cols[col_idx]:
            # Day number
            st.markdown(f"**{day_num}**")
            
            # Events on this day
            if day_num in days_events:
                for event in days_events[day_num][:3]:  # Show max 3 events per day
                    tournament = event.get('tournament_name', '')[:15]  # Truncate
                    st.caption(f"• {tournament}")
                
                if len(days_events[day_num]) > 3:
                    st.caption(f"... +{len(days_events[day_num]) - 3} mais")
        
        day_of_week = (day_of_week + 1) % 7
        if day_of_week == 0:
            st.markdown("")
            week_cols = st.columns(7)
        
        current_day += timedelta(days=1)
        day_num += 1


def render_event_timeline(events: List[Dict[str, Any]], days_ahead: int = 7):
    """
    Render a timeline of upcoming events.
    
    Args:
        events: List of event dictionaries
        days_ahead: Number of days to show
    """
    if not events:
        st.info("Nenhum evento nos próximos dias.")
        return
    
    # Group events by date
    today = datetime.now().date()
    timeline_events = {}
    
    for event in events:
        start_time = event.get('start_time')
        if isinstance(start_time, str):
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                continue
        else:
            start_dt = start_time
        
        if not start_dt:
            continue
        
        event_date = start_dt.date()
        days_diff = (event_date - today).days
        
        if 0 <= days_diff <= days_ahead:
            date_key = event_date.strftime('%Y-%m-%d')
            if date_key not in timeline_events:
                timeline_events[date_key] = []
            timeline_events[date_key].append({
                **event,
                'start_dt': start_dt
            })
    
    # Display timeline
    for date_str in sorted(timeline_events.keys()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        days_from_now = (date_obj - today).days
        
        if days_from_now == 0:
            date_label = "🔥 Hoje"
        elif days_from_now == 1:
            date_label = "📅 Amanhã"
        else:
            date_label = f"📅 {date_obj.strftime('%d/%m/%Y')}"
        
        st.markdown(f"### {date_label}")
        
        day_events = timeline_events[date_str]
        for event in sorted(day_events, key=lambda x: x['start_dt']):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                time_str = event['start_dt'].strftime('%H:%M')
                st.markdown(f"**{time_str}**")
            
            with col2:
                team1 = event.get('team1', 'Team 1')
                team2 = event.get('team2', 'Team 2')
                tournament = event.get('tournament_name', '')
                st.markdown(f"{team1} vs {team2}")
                st.caption(tournament)
            
            with col3:
                sport = event.get('sport_name', '')
                st.caption(sport)
        
        st.markdown("---")


def render_tournament_list(
    tournaments: List[Dict[str, Any]],
    tier_filter: Optional[str] = None
):
    """
    Render a list of tournaments with filters.
    
    Args:
        tournaments: List of tournament dictionaries
        tier_filter: Optional tier filter (S, A, B, C)
    """
    if not tournaments:
        st.info("Nenhum torneio encontrado.")
        return
    
    # Filter by tier if specified
    if tier_filter:
        tournaments = [t for t in tournaments if t.get('tier') == tier_filter]
    
    # Group by sport
    sports = {}
    for tournament in tournaments:
        sport = tournament.get('sport_name', 'Unknown')
        if sport not in sports:
            sports[sport] = []
        sports[sport].append(tournament)
    
    # Display by sport
    for sport, sport_tournaments in sports.items():
        with st.expander(f"**{sport}** ({len(sport_tournaments)} torneios)"):
            for tournament in sport_tournaments:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    name = tournament.get('tournament_name', '')
                    region = tournament.get('region', '')
                    st.markdown(f"• **{name}**")
                    if region:
                        st.caption(f"Região: {region}")
                
                with col2:
                    tier = tournament.get('tier', 'N/A')
                    tier_color = {
                        'S': '#FFD700',
                        'A': '#C0C0C0',
                        'B': '#CD7F32',
                        'C': '#808080',
                    }.get(tier, '#6c757d')
                    st.markdown(
                        f'<span style="color: {tier_color}; font-weight: bold;">Tier {tier}</span>',
                        unsafe_allow_html=True
                    )
