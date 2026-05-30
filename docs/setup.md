# Installation

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) or pip
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Alpaca account ([paper](https://app.alpaca.markets) for testing)

## Python Setup

```bash
# Clone the repository
git clone https://github.com/komelImoet/JatayuCore.git
cd JatayuCore

# Install with uv (recommended)
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Telegram Bot Setup

1. Open [@BotFather](https://t.me/botfather) in Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
5. Add to `.env`:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmNOPqrstUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Alpaca Broker Setup

1. Register at [alpaca.markets](https://alpaca.markets) (free, 5 minutes)
2. Switch to **Paper** trading (top-right toggle in web app)
3. Go to API Keys section → **Generate Key**
4. Add to `.env`:

```bash
ALPACA_API_KEY=PK1234567890ABCDEFGH
ALPACA_SECRET_KEY=sk1234567890abcdefghijklmnopqrstuvwxyz
```

## LLM Provider

Set at least one LLM provider in `.env`:

```bash
# DeepSeek (cheapest, recommended)
DEEPSEEK_API_KEY=sk-...

# Or OpenAI
OPENAI_API_KEY=sk-...
```

## Verify Installation

```bash
# Single analysis (no trade, just signal)
uv run python main.py run NVDA --date 2025-05-30

# Expected: Buy / Overweight / Hold / Underweight / Sell
```

## Docker Setup

```bash
# Copy config
cp .env.example .env
# Edit .env with your API keys

# Run scheduler
docker compose up -d jatayucore
```

## Scheduler (Background)

```bash
# Run once (foreground)
uv run python main.py schedule --tickers AAPL,NVDA,MSFT

# Run as daemon (background)
uv run python main.py schedule -D --tickers AAPL,NVDA,MSFT

# Or with screen
screen -S jatayu
uv run python main.py schedule --tickers AAPL,NVDA,MSFT
# Ctrl+A D to detach, screen -r jatayu to reattach
```
