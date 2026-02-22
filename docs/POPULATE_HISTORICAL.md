# Populamento Histórico

## O que é?
Script para popular o database com TODO o histórico disponível no Scorealarm.

## Características
- 🐢 **Rate limit gentil**: 10 req/min para não forçar o servidor
- 💾 **Checkpoint**: Salva progresso, pode interromper e continuar
- 🌙 **Modo noturno**: 50% mais rápido entre 02h-06h UTC
- ⏱️ **Duração**: 4-8 horas (só roda UMA vez)

## Como usar

### Rodar populamento
```bash
# Continua de onde parou (ou inicia se primeira vez)
python run_populate_historical.py

# Recomeça do zero
python run_populate_historical.py --fresh

# Ver status
python run_populate_historical.py --status
```

### Rodar em background
```bash
nohup python run_populate_historical.py > logs/populate.log 2>&1 &

# Acompanhar
tail -f logs/populate.log
```

## Configuração

Edite `jobs/populate_historical.py` para ajustar:

```python
self.limiter = GentleRateLimiter(
    requests_per_minute=10,      # Requests por minuto
    delay_between_requests=3.0,  # Segundos entre requests
    delay_between_sports=30,     # Pausa entre esportes
    delay_between_tournaments=5, # Pausa entre torneios
    night_mode_speedup=True      # Mais rápido de madrugada
)
```

## Checkpoint

O checkpoint é salvo em `data/populate_checkpoint.json`:

```json
{
  "completed_tournaments": [123, 456, 789],
  "completed_sports": [1, 2, 3],
  "stats": {
    "sports": 10,
    "tournaments": 150,
    "seasons": 300,
    "matches": 50000,
    "errors": 5
  },
  "last_updated": "2024-01-15T10:30:00"
}
```

## Após completar

O database terá:
- Todos os esportes
- Todos os torneios
- Todas as temporadas
- Todos os jogos históricos
- Times com ratings inicializados

Isso alimenta o sistema de ML e ELO para calcular probabilidades precisas.
