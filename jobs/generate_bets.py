"""Generate bet suggestions job."""
from datetime import datetime
from typing import List, Dict
import random
from utils.logger import log
from edge.finder import EdgeFinder
from betting.generator import BetGenerator
from notifications.notifications import notification_system
from scrapers.hltv_scraper import HLTVScraper
from scrapers.vlr import VLRScraper
from database.db import get_db
from database.models import Match, Prediction


def generate_bets_job():
    """Job to generate bet suggestions."""
    try:
        log.info("Starting bet generation job")
        
        # 1. Fetch upcoming matches from scrapers
        log.info("Fetching matches from scrapers...")
        hltv = HLTVScraper()
        vlr = VLRScraper()
        
        cs2_matches = hltv.fetch_matches()
        valorant_matches = vlr.fetch_matches()
        
        all_matches = cs2_matches + valorant_matches
        log.info(f"Found {len(all_matches)} matches ({len(cs2_matches)} CS2, {len(valorant_matches)} Valorant)")
        
        if not all_matches:
            log.warning("No matches found")
            return
        
        # 2. Save matches to database
        log.info("Saving matches to database...")
        saved_matches = _save_matches_to_db(all_matches)
        log.info(f"Saved {len(saved_matches)} matches to database")
        
        # 3. Generate predictions (simple model for now)
        log.info("Generating predictions...")
        predictions = _generate_predictions(saved_matches)
        log.info(f"Generated {len(predictions)} predictions")
        
        # 4. Create mock odds data
        log.info("Generating mock odds data...")
        odds_data = _generate_mock_odds(saved_matches)
        
        # 5. Find edges
        log.info("Finding betting edges...")
        edge_finder = EdgeFinder()
        opportunities = edge_finder.scan_opportunities(predictions, odds_data)
        log.info(f"Found {len(opportunities)} betting opportunities")
        
        # 6. Generate bet suggestions
        if opportunities:
            # Enrich opportunities with match data
            enriched_opportunities = _enrich_opportunities(opportunities, saved_matches)
            
            bet_generator = BetGenerator()
            bets = bet_generator.generate_bets(enriched_opportunities)
            bet_generator.save_bets(bets)
            
            log.info(f"Generated {len(bets)} bet suggestions")
            
            # 7. Send notifications
            log.info("Sending notifications...")
            notification_system.notify_opportunities(enriched_opportunities)
            log.info("Notifications sent")
        else:
            log.info("No betting opportunities found")
            
    except Exception as e:
        log.error(f"Error in bet generation job: {e}", exc_info=True)


def _save_matches_to_db(matches: List[Dict]) -> List[Match]:
    """Save matches to database.
    
    Args:
        matches: List of match dictionaries
        
    Returns:
        List of saved Match objects (as dictionaries with IDs)
    """
    saved_matches = []
    
    with get_db() as db:
        for match_data in matches:
            # Check if match already exists
            existing = db.query(Match).filter(
                Match.game == match_data['game'],
                Match.team1 == match_data['team1'],
                Match.team2 == match_data['team2'],
                Match.start_time == match_data['start_time']
            ).first()
            
            if existing:
                log.debug(f"Match already exists: {match_data['team1']} vs {match_data['team2']}")
                saved_matches.append({
                    'id': existing.id,
                    'game': existing.game,
                    'team1': existing.team1,
                    'team2': existing.team2,
                    'start_time': existing.start_time,
                    'tournament': existing.tournament,
                    'best_of': existing.best_of,
                })
                continue
            
            match = Match(
                game=match_data['game'],
                team1=match_data['team1'],
                team2=match_data['team2'],
                start_time=match_data['start_time'],
                tournament=match_data.get('tournament'),
                best_of=match_data.get('best_of', 1),
            )
            db.add(match)
            db.flush()  # Get the ID
            saved_matches.append({
                'id': match.id,
                'game': match.game,
                'team1': match.team1,
                'team2': match.team2,
                'start_time': match.start_time,
                'tournament': match.tournament,
                'best_of': match.best_of,
            })
            log.debug(f"Saved match: {match.team1} vs {match.team2}")
    
    return saved_matches


def _generate_predictions(matches: List[Dict]) -> List[Dict]:
    """Generate simple predictions for matches.
    
    For now, uses a simple random model with slight bias.
    In the future, this would use actual ML models.
    
    Args:
        matches: List of match dictionaries with 'id' field
        
    Returns:
        List of prediction dictionaries
    """
    predictions = []
    
    with get_db() as db:
        for match in matches:
            match_id = match['id']
            
            # Simple prediction: random with slight variance
            # Team 1 probability between 40-60%
            team1_prob = random.uniform(0.40, 0.60)
            team2_prob = 1.0 - team1_prob
            
            # Save prediction to database
            prediction = Prediction(
                match_id=match_id,
                model_type='simple_random',
                team1_win_prob=team1_prob,
                team2_win_prob=team2_prob,
            )
            db.add(prediction)
            
            predictions.append({
                'match_id': match_id,
                'team1_win_prob': team1_prob,
                'team2_win_prob': team2_prob,
                'model': 'simple_random',
            })
            
            log.debug(f"Generated prediction for {match['team1']} vs {match['team2']}: {team1_prob:.2%} - {team2_prob:.2%}")
    
    return predictions


def _generate_mock_odds(matches: List[Dict]) -> List[Dict]:
    """Generate mock odds data for testing.
    
    Args:
        matches: List of match dictionaries with 'id' field
        
    Returns:
        List of odds dictionaries
    """
    odds_data = []
    bookmakers = ['Pinnacle', 'bet365', 'Betfair', 'Rivalry']
    
    for match in matches:
        match_id = match['id']
        
        for bookmaker in bookmakers:
            # Generate odds that are slightly worse than fair
            # This creates opportunities when our model is confident
            margin = random.uniform(1.03, 1.08)  # 3-8% margin
            
            # Base fair odds (inverse of ~50/50)
            base_team1_odds = random.uniform(1.80, 2.20)
            base_team2_odds = random.uniform(1.80, 2.20)
            
            # Apply margin
            team1_odds = base_team1_odds * margin
            team2_odds = base_team2_odds * margin
            
            odds_data.append({
                'match_id': match_id,
                'bookmaker': bookmaker,
                'market_type': 'match_winner',
                'team1_odds': team1_odds,
                'team2_odds': team2_odds,
            })
    
    return odds_data


def _enrich_opportunities(opportunities: List[Dict], matches: List[Dict]) -> List[Dict]:
    """Enrich opportunities with match details for notifications.
    
    Args:
        opportunities: List of opportunity dictionaries
        matches: List of match dictionaries
        
    Returns:
        List of enriched opportunity dictionaries
    """
    match_dict = {m['id']: m for m in matches}
    enriched = []
    
    for opp in opportunities:
        match_id = opp.get('match_id')
        match = match_dict.get(match_id)
        
        if not match:
            continue
        
        enriched_opp = {
            **opp,
            'team1': match['team1'],
            'team2': match['team2'],
            'game': match['game'],
            'tournament': match['tournament'],
            'start_time': match['start_time'],
            'stake': 100,  # Default stake
        }
        enriched.append(enriched_opp)
    
    return enriched


if __name__ == '__main__':
    # Initialize database
    from database.db import init_db
    init_db()
    
    # Run the job
    generate_bets_job()
