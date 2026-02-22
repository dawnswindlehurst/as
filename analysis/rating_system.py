"""Sistema de Rating (ELO/Glicko) para calcular força dos times."""


class EloRating:
    """Sistema ELO para calcular força dos times."""
    
    K_FACTOR = 32
    DEFAULT_RATING = 1500
    
    def calculate_expected(self, rating_a: float, rating_b: float) -> float:
        """Calcula probabilidade esperada de A vencer B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, rating_a: float, rating_b: float, result: float) -> tuple:
        """Atualiza ratings após partida. result: 1=A venceu, 0=B venceu, 0.5=empate"""
        expected_a = self.calculate_expected(rating_a, rating_b)
        expected_b = 1 - expected_a
        
        new_rating_a = rating_a + self.K_FACTOR * (result - expected_a)
        new_rating_b = rating_b + self.K_FACTOR * ((1 - result) - expected_b)
        
        return new_rating_a, new_rating_b


class GlickoRating:
    """Sistema Glicko-2 (mais preciso que ELO)."""
    
    def __init__(self):
        self.default_rating = 1500
        self.default_rd = 350  # Rating deviation
        self.default_vol = 0.06  # Volatility
        self.tau = 0.5  # System constant
    
    def calculate_expected(self, rating: float, rd: float, opponent_rating: float, opponent_rd: float) -> float:
        """Calcula probabilidade esperada considerando incerteza."""
        g_rd = self._g(opponent_rd)
        return 1 / (1 + 10 ** (-g_rd * (rating - opponent_rating) / 400))
    
    def _g(self, rd: float) -> float:
        """Função auxiliar g(RD) do Glicko-2."""
        import math
        q = math.log(10) / 400
        return 1 / math.sqrt(1 + 3 * q**2 * rd**2 / math.pi**2)
    
    def update_rating(self, rating: float, rd: float, vol: float, 
                     opponent_rating: float, opponent_rd: float, result: float) -> tuple:
        """Atualiza rating Glicko-2.
        
        Args:
            rating: Rating atual do jogador
            rd: Rating deviation atual
            vol: Volatility atual
            opponent_rating: Rating do oponente
            opponent_rd: RD do oponente
            result: Resultado (1=vitória, 0.5=empate, 0=derrota)
            
        Returns:
            Tuple com (novo_rating, novo_rd, novo_vol)
        """
        import math
        
        # Conversão para escala Glicko-2
        mu = (rating - 1500) / 173.7178
        phi = rd / 173.7178
        mu_j = (opponent_rating - 1500) / 173.7178
        phi_j = opponent_rd / 173.7178
        
        # Cálculo de g e E
        g = self._g(phi_j * 173.7178)
        E = self.calculate_expected(rating, rd, opponent_rating, opponent_rd)
        
        # Variância estimada
        v = 1 / (g**2 * E * (1 - E))
        
        # Delta
        delta = v * g * (result - E)
        
        # Nova volatilidade (simplificado)
        new_vol = vol
        
        # Novo RD
        phi_star = math.sqrt(phi**2 + new_vol**2)
        new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        
        # Novo rating
        new_mu = mu + new_phi**2 * g * (result - E)
        
        # Conversão de volta para escala original
        new_rating = new_mu * 173.7178 + 1500
        new_rd = new_phi * 173.7178
        
        return new_rating, new_rd, new_vol
