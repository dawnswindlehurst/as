"""Configuration for bookmaker scrapers."""

BOOKMAKERS_CONFIG = {
    # ATIVAS
    "superbet": {
        "enabled": True,
        "type": "scraper",
        "category": "traditional",
        "base_url": "https://superbet.com",
        "priority": 1
    },
    "stake": {
        "enabled": True,
        "type": "api",
        "category": "crypto",
        "base_url": "https://stake.com",
        "api_docs": "https://docs.stake.com/",
        "priority": 1
    },
    
    # TRADICIONAIS - DESABILITADAS
    "bet365": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "betano": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "sportingbet": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "betfair": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "1xbet": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "pinnacle": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    "kto": {
        "enabled": False,
        "type": "scraper",
        "category": "traditional",
        "status": "aguardando_configuracao"
    },
    
    # CRYPTO - DESABILITADAS
    "bcgame": {
        "enabled": False,
        "type": "scraper",
        "category": "crypto",
        "status": "verificar_api"
    },
    "cloudbet": {
        "enabled": False,
        "type": "scraper",
        "category": "crypto",
        "status": "verificar_api"
    },
    "spartans": {
        "enabled": False,
        "type": "scraper",
        "category": "crypto",
        "status": "verificar_api"
    },
    "thunderpick": {
        "enabled": False,
        "type": "scraper",
        "category": "crypto",
        "status": "verificar_api"
    },
}


def get_enabled_bookmakers():
    """Get list of enabled bookmakers.
    
    Returns:
        List of enabled bookmaker names
    """
    return [name for name, config in BOOKMAKERS_CONFIG.items() if config.get("enabled", False)]


def get_bookmaker_config(name: str):
    """Get configuration for a specific bookmaker.
    
    Args:
        name: Bookmaker name
        
    Returns:
        Configuration dictionary or None
    """
    return BOOKMAKERS_CONFIG.get(name)


def get_bookmakers_by_category(category: str):
    """Get bookmakers by category.
    
    Args:
        category: 'traditional' or 'crypto'
        
    Returns:
        Dictionary of bookmakers in the category
    """
    return {
        name: config
        for name, config in BOOKMAKERS_CONFIG.items()
        if config.get("category") == category
    }
