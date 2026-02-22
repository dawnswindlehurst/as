# Dashboard + Notificações

## Dashboard

### Iniciar
```bash
python run_dashboard.py
```

Acesse: http://localhost:8000

### Páginas
- `/` - Home com stats gerais
- `/opportunities` - Top oportunidades de apostas
- `/sports` - Stats por esporte
- `/bets` - Lista de apostas

### API
- `GET /api/stats` - Stats em JSON
- `GET /api/opportunities` - Oportunidades em JSON

## Notificações

### Telegram
1. Crie um bot com @BotFather
2. Pegue o token
3. Pegue seu chat_id com @userinfobot
4. Configure no .env:
```env
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
```

### Discord
1. Crie um webhook no canal
2. Configure no .env:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy
```

## Alertas

### Oportunidades (edge > 5%)
Receba alertas automáticos quando detectamos apostas com edge alto.

### Resumo Diário (21h UTC)
Receba resumo diário com:
- Profit do dia
- Win rate
- Top esporte
- Apostas pendentes

## Arquitetura

### Dashboard Web (FastAPI)
O dashboard é uma aplicação FastAPI que serve páginas HTML usando Jinja2 templates e Bootstrap para estilização.

**Componentes:**
- `dashboard/app.py` - Aplicação FastAPI principal com rotas
- `dashboard/templates/` - Templates HTML Jinja2
- `dashboard/static/` - Arquivos CSS e outros recursos estáticos

### Sistema de Notificações

**Arquitetura:**
```
NotificationProvider (ABC)
  ├── TelegramNotifier - Implementa envio via API do Telegram
  └── DiscordNotifier - Implementa envio via Discord Webhooks

NotificationManager - Gerencia múltiplos providers
```

**Integração:**
- Paper Trading Job detecta oportunidades e notifica via NotificationManager
- Suporte para múltiplos canais simultaneamente (Telegram + Discord)
- Configuração via variáveis de ambiente

### Jobs

**PaperTradingJob:**
1. Sincroniza jogos
2. Atualiza ratings
3. Liquida apostas finalizadas
4. Detecta oportunidades
5. **NOVO:** Notifica oportunidades com edge > 5%
6. Registra novas apostas

**DailySummaryJob:**
- Roda às 21h UTC
- Calcula estatísticas do dia
- Envia resumo via todos os canais configurados

## Uso

### Rodar Dashboard
```bash
python run_dashboard.py
```

### Rodar Paper Trading com Notificações
```bash
python run_paper_trading.py
```

### Testar Notificações
```python
from notifications.manager import NotificationManager
import asyncio

async def test():
    notifier = NotificationManager()
    
    # Testar oportunidade
    opp = {
        'match_name': 'Team A vs Team B',
        'bet_on': 'team1',
        'odds': 2.5,
        'edge': 0.08,
        'our_probability': 0.5,
        'implied_probability': 0.4
    }
    
    await notifier.notify_opportunity(opp, min_edge=0.05)

asyncio.run(test())
```

## Troubleshooting

### Telegram não envia mensagens
- Verifique se o bot_token está correto
- Verifique se o chat_id está correto
- Teste enviando mensagem diretamente via curl:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### Discord webhook não funciona
- Verifique se a URL do webhook está completa
- Teste o webhook diretamente:
```bash
curl -X POST "<WEBHOOK_URL>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test"}'
```

### Dashboard não inicia
- Verifique se todas as dependências estão instaladas: `pip install fastapi uvicorn jinja2`
- Verifique se a porta 8000 está disponível
- Verifique os logs para erros de conexão com o banco de dados
