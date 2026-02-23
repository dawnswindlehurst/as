"""
Sport mapping between Superbet IDs and our database.
Based on actual events found.
"""

# Superbet Sport IDs -> Nome (corrigido com base nos eventos reais)
SUPERBET_SPORTS = {
    1: "Vôlei",
    2: "Tênis",
    3: "Hóquei no Gelo",
    4: "Basquete",
    5: "Futebol",
    6: "Sinuca/Snooker",
    11: "Handebol",
    13: "Dardos",
    17: "Futsal",
    20: "Beisebol",  # Corrigido! Era listado como Futebol Americano
    24: "Tênis de Mesa",
    32: "Críquete",
    39: "League of Legends",
    54: "Dota 2",
    55: "Counter-Strike 2",
    153: "Valorant",
}

# Esportes úteis para coleta
ALL_SPORTS = [1, 2, 3, 4, 5, 6, 11, 13, 17, 20, 24, 32, 39, 54, 55, 153]

# Esportes prioritários (principais com mais mercados)
PRIORITY_SPORTS = [4, 5, 2, 3, 1]  # Basquete, Futebol, Tênis, Hóquei, Vôlei

# Nosso banco -> Superbet Sport ID
DB_TO_SUPERBET = {
    "Futebol": 5,
    "Basquete": 4,
    "Tênis": 2,
    "Vôlei": 1,
    "Hóquei no Gelo": 3,
    "Handebol": 11,
    "Beisebol": 20,
    "Dardos": 13,
    "Tênis de Mesa": 24,
    "Futsal": 17,
    "Sinuca": 6,
    "Críquete": 32,
    "League of Legends": 39,
    "Dota 2": 54,
    "Counter-Strike 2": 55,
    "CS:GO": 55,
}

# Esportes que suportam player props
SPORTS_WITH_PLAYER_PROPS = {
    4,   # Basquete
    5,   # Futebol
    3,   # Hóquei no Gelo
}


def get_superbet_sport_id(db_sport: str) -> int | None:
    return DB_TO_SUPERBET.get(db_sport)


def get_sport_name(superbet_id: int) -> str:
    return SUPERBET_SPORTS.get(superbet_id, f"Unknown ({superbet_id})")


def supports_player_props(sport_id: int) -> bool:
    return sport_id in SPORTS_WITH_PLAYER_PROPS
