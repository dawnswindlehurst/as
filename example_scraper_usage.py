"""Example usage of the modular scraper system.

This script demonstrates how to:
1. Register scrapers
2. List all available scrapers
3. Check health of enabled scrapers
4. Fetch odds from enabled scrapers
5. Compare odds across bookmakers
"""
import asyncio
from scrapers.scraper_manager import scraper_manager
from scrapers.config import BOOKMAKERS_CONFIG

# Import active scrapers
from scrapers.active.superbet import SuperbetScraper
from scrapers.active.stake import StakeScraper

# Import disabled scrapers (for demonstration)
from scrapers.traditional.bet365 import Bet365Scraper
from scrapers.traditional.betano import BetanoScraper
from scrapers.crypto.bcgame import BCGameScraper


async def main():
    """Main example function."""
    
    print("=" * 80)
    print("MODULAR SCRAPER SYSTEM - EXAMPLE")
    print("=" * 80)
    print()
    
    # 1. Register scrapers
    print("1. Registering scrapers...")
    print("-" * 80)
    
    # Register active scrapers
    scraper_manager.register_scraper(SuperbetScraper())
    scraper_manager.register_scraper(StakeScraper())
    
    # Register some disabled scrapers for demonstration
    scraper_manager.register_scraper(Bet365Scraper())
    scraper_manager.register_scraper(BetanoScraper())
    scraper_manager.register_scraper(BCGameScraper())
    
    print()
    
    # 2. List all scrapers
    print("2. All registered scrapers:")
    print("-" * 80)
    all_scrapers = scraper_manager.list_all_scrapers()
    for name, info in all_scrapers.items():
        status_icon = "✅" if info['enabled'] else "⏸️"
        print(f"{status_icon} {name:15} | Type: {info['type']:8} | Category: {info['category']:11} | Status: {info['status']}")
    print()
    
    # 3. Show enabled scrapers only
    print("3. Enabled scrapers:")
    print("-" * 80)
    enabled = scraper_manager.get_enabled_scrapers()
    for scraper in enabled:
        print(f"✅ {scraper.name} - {scraper.integration_type.value}")
    print()
    
    # 4. Health check
    print("4. Health check for enabled scrapers:")
    print("-" * 80)
    health_status = await scraper_manager.health_check_all()
    for name, is_healthy in health_status.items():
        status = "✓ OK" if is_healthy else "✗ FAILED"
        print(f"{name:15} : {status}")
    print()
    
    # 5. Fetch odds (will be empty since we haven't implemented the actual scraping yet)
    print("5. Fetching odds from enabled scrapers:")
    print("-" * 80)
    try:
        all_odds = await scraper_manager.fetch_all_odds(game="cs2")
        for bookmaker, odds_list in all_odds.items():
            print(f"{bookmaker:15} : {len(odds_list)} odds found")
    except Exception as e:
        print(f"Note: Odds fetching returned empty results (expected - scrapers need implementation)")
    print()
    
    # 6. Try to use a disabled scraper (will raise NotImplementedError)
    print("6. Attempting to use a disabled scraper:")
    print("-" * 80)
    bet365 = scraper_manager.get_scraper("bet365")
    if bet365:
        try:
            await bet365.get_esports_odds()
        except NotImplementedError as e:
            print(f"Expected error: {e}")
    print()
    
    # 7. Show configuration
    print("7. Bookmaker configuration:")
    print("-" * 80)
    print(f"Total configured bookmakers: {len(BOOKMAKERS_CONFIG)}")
    active_count = sum(1 for cfg in BOOKMAKERS_CONFIG.values() if cfg.get('enabled'))
    disabled_count = len(BOOKMAKERS_CONFIG) - active_count
    print(f"Active: {active_count}")
    print(f"Disabled: {disabled_count}")
    print()
    
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
