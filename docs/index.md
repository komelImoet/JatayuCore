# JatayuCore

<p align="center">
  <img src="../assets/jatayucore.svg" alt="JatayuCore" width="480">
</p>

**Multi-Agent AI Trading Framework** — Terinspirasi dari Jatayu, elang mitologis yang memiliki visi tajam, ketepatan, dan kesetiaan.

```mermaid
flowchart TB
    subgraph Jatayu["🦅 JatayuCore"]
        direction TB
        V[👁️ Visi Tajam<br/>Multi-Agent AI] --> P[🎯 Ketepatan<br/>Risk Management]
        P --> K[🪽 Kekuatan<br/>Eksekusi Otomatis]
        K --> S[💪 Kesetiaan<br/>Telegram 24/7]
    end
    style Jatayu fill:#fff3e0,stroke:#e65100,color:#000
```

## Pipeline

```mermaid
flowchart LR
    subgraph Core["🐍 JatayuCore"]
        TA[Jatayu Agent Pipeline<br/>Analis → Debat → Eksekusi]
    end
    subgraph Broker["💹 Alpaca Broker"]
        AP[Paper / Live Trading<br/>Market Orders]
    end
    subgraph Monitor["📡 Background Monitor"]
        SL[Stop Loss 5%]
        SUM[Position Summary /jam]
        HB[Heartbeat /2jam]
    end
    subgraph Telegram["📱 Telegram"]
        TG[Bot: Signal + Eksekusi<br/>+ Error + Report]
    end

    TA -->|Buy/Overweight| AP
    TA -->|Sell/Underweight| AP
    TA --> TG
    AP --> TG
    Monitor --> SL -->|Price turun 5%| AP
    Monitor --> SUM --> TG
    Monitor --> HB --> TG

    style Core fill:#e3f2fd,stroke:#1565c0,color:#000
    style Broker fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Monitor fill:#fff3e0,stroke:#e65100,color:#000
    style Telegram fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

## Fitur

- **Auto Execution** — Buy/Sell otomatis ke [Alpaca](https://alpaca.markets) (paper/live)
- **Stop Loss Guard** — Background thread auto close posisi kalo turun 5%
- **Position Summary** — Laporan posisi + P&L tiap jam ke Telegram
- **Daily P&L Report** — Rekap portfolio tiap hari
- **Health Heartbeat** — Bot ngasih tau "saya masih hidup" tiap 2 jam
- **Weekend Skip** — Gak jalan di Sabtu/Minggu
- **Daemon Mode** — `python main.py schedule -D` jalan di background

## Start Cepat

```bash
git clone https://github.com/komelImoet/JatayuCore.git
cd JatayuCore

# Setup Telegram + Alpaca
export TELEGRAM_BOT_TOKEN="token_lo"
export TELEGRAM_CHAT_ID="chat_id_lo"
export ALPACA_API_KEY="paper_key_lo"
export ALPACA_SECRET_KEY="paper_secret_lo"

# Analisis + auto execute
uv run python main.py run AAPL

# Scheduler background (otomatis tiap hari)
uv run python main.py schedule -D --tickers AAPL,NVDA,MSFT
```

---

*"Terbang tinggi, sambar tepat, pantang menyerah."* — JatayuCore
