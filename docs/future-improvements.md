# Future Improvements

Ide dan roadmap untuk pengembangan JatayuCore selanjutnya.

## Broker & Execution

### ✅ Alpaca Integration (Next Up)
- [ ] Implement `AlpacaBroker` — place market/limit orders via Alpaca REST API
- [ ] Paper trading mode (free, real market data, no real money)
- [ ] Position tracking & portfolio sync
- [ ] Auto-execution based on rating: Buy/Overweight → market order

### 🔜 Windows + MT5 Execution
- [ ] WSL2 setup guide for Windows 24/7 operation
- [ ] Python bridge script (Windows native → MT5)
- [ ] Auto-start scheduler via Windows Task Scheduler
- [ ] MT5 journal parsing for fill confirmation
- [ ] Graceful failover between Alpaca ↔ MT5

### 🔮 Other Brokers
- [ ] Interactive Brokers (IBKR) via `ib_insync`
- [ ] Binance / Bybit for crypto trading
- [ ] Broker-agnostic order router

## Multi-Asset Support

- [ ] **Crypto** — 24/7 market, different risk profile
- [ ] **Forex** — pairs, leverage, rollover
- [ ] **Options** — covered calls, protective puts, spreads
- [ ] **ETF** — sector rotation analysis
- [ ] **Bonds / Commodities** — macro diversification

## Risk Management

- [ ] Dynamic position sizing based on Kelly Criterion
- [ ] Portfolio correlation heatmap (avoid overconcentration)
- [ ] Max drawdown circuit breaker (pause trading)
- [ ] Daily loss limit (% of P&L)
- [ ] Time-based stop loss (e.g., close all EOD Friday)
- [ ] Max open positions at once

## Monitoring & UI

- [ ] **Web Dashboard** — Flask/FastAPI + Chart.js — lihat positions, P&L, trading history
- [ ] **Live P&L** — real-time portfolio value pushed to Telegram
- [ ] **Manual Override** — Telegram inline buttons: Approve / Reject / Modify order
- [ ] **Trade Journal** — Markdown log with annotated charts
- [ ] **Backtesting Dashboard** — visualize historical signals vs actual performance

## AI / LLM Enhancements

- [ ] **Multi-model voting** — 3 different LLMs vote, majority wins
- [ ] **Fine-tuned model** — LoRA adapters based on historical trade outcomes
- [ ] **On-chain data** for crypto sentiment (Glassnode, Dune)
- [ ] **Alternative data** — SEC filings parsing, insider transaction tracking
- [ ] **Earnings calendar awareness** — skip analysis during blackout windows

## Data Vendors

| Vendor | What It Adds | Cost |
|--------|-------------|------|
| Polygon.io | Real-time + historical, webhook-ready | $29–199/mo |
| Alpha Vantage | Fundamental data, FX, crypto | Free / $50 |
| Finnhub | News sentiment, earnings, SEC filings | Free / $9 |
| TradingView Webhook | Price alerts, indicator crossings | Free |

## Scheduler & Reliability

- [ ] Retry logic on failure (max 3 attempts before skip)
- [ ] Heartbeat monitoring (ping Telegram every N hours)
- [ ] Graceful shutdown — complete current ticker, save state
- [ ] Multi-timezone support (bypass for now)
- [ ] Webhook mode — TradingView alert → trigger analysis immediately

## Deployment

- [ ] **GitHub Actions CI** — lint, typecheck, test on push
- [ ] **Systemd service** — proper daemon management (restart, logs)
- [ ] **Healthcheck endpoint** — Docker compose health status
- [ ] **Secrets management** — Docker secrets or HashiCorp Vault
- [ ] **Log aggregation** — push logs to Loki / DataDog
- [ ] **Auto-update** — `git pull` + restart on new release

## Documentation

- [ ] Video tutorial — setup + first trade in 10 minutes
- [ ] FAQ page — common issues & solutions
- [ ] Performance benchmarks — which LLM/cost/speed for each agent
- [ ] Strategy cookbook — example configs for different styles

## Experimental / Research

- [ ] **Reinforcement Learning** — agent learns from realized P&L feedback
- [ ] **Market Regime Detection** — switch strategy based on trending vs ranging markets
- [ ] **Order Book Imbalance** — micro-structure signals (if data available)
- [ ] **Cross-asset correlation trading** — e.g., NVDA ↔ SOX, BTC ↔ MSTR

---

*Punya ide lain? Buka issue di [GitHub](https://github.com/komelImoet/JatayuCore/issues).*
