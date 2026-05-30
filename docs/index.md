# TradingAgents

**Multi-Agent LLM Financial Trading Framework** with automated MetaTrader 5 execution and real-time Telegram notifications.

## Overview

TradingAgents orchestrates a team of AI-powered analyst agents that research, debate, and produce trading decisions.

```mermaid
flowchart LR
    subgraph Python["🐍 Python Layer"]
        TA[TradingAgents<br/>Multi-Agent Pipeline] -->|JSON File| JS[(State Log)]
    end
    
    subgraph Rust["🦀 Rust Layer"]
        JS --> WE[Watcher Engine]
        WE --> RM[Risk Manager]
        RM --> OC[MT5 Connector]
    end
    
    subgraph MT5["💹 MetaTrader 5"]
        OC -->|JSON-RPC| MT[MT5 Terminal]
        MT -->|MQL EA| TG1[📱 Telegram]
    end
    
    TA -.->|HTTP| TG2[📱 Telegram]
    WE -.->|HTTP| TG2
    
    style Python fill:#e3f2fd,stroke:#1565c0
    style Rust fill:#fff3e0,stroke:#e65100
    style MT5 fill:#e8f5e9,stroke:#2e7d32
```

## Pipeline Flow

```mermaid
flowchart TB
    subgraph Analysis["🔬 Analysis Phase"]
        A1[📈 Market Analyst] --> D[🤖 AI Team Debate]
        A2[📰 News Analyst] --> D
        A3[💬 Social Analyst] --> D
        A4[📋 Fundamentals Analyst] --> D
    end
    
    subgraph Research["📝 Research Phase"]
        D --> BULL[🐂 Bull Case]
        D --> BEAR[🐻 Bear Case]
        BULL --> PM[Portfolio Manager]
        BEAR --> PM
    end
    
    subgraph Execution["⚡ Execution Phase"]
        PM --> DECISION{Decision}
        DECISION -->|Buy/Overweight| TRADE[📈 Execute Trade]
        DECISION -->|Hold| SKIP[⏭️ Skip]
        DECISION -->|Underweight/Sell| TRADE2[📉 Reduce/Exit]
    end
    
    subgraph Notify["🔔 Notification Phase"]
        TRADE --> TG[📱 Telegram Alert]
        SKIP --> TG
        TRADE2 --> TG
    end
    
    style Analysis fill:#e3f2fd
    style Research fill:#f3e5f5
    style Execution fill:#e8f5e9
    style Notify fill:#fce4ec
```

## Features

- **Multi-Agent AI Pipeline** — 7 specialized agents collaborate on each decision
- **MetaTrader 5 Integration** — Automated order execution via Rust bridge
- **Telegram Alerts** — Real-time notifications at every stage
- **Scheduler** — Fully automated daily trading sessions
- **Risk Management** — Configurable position sizing, exposure limits, stop-loss enforcement
- **Docker Support** — Deploy the entire stack with Docker Compose

## Quick Start

```bash
# Clone the repo
git clone https://github.com/komelImoet/TradingAgents.git
cd TradingAgents

# Set up Telegram (optional)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run single analysis
python main.py run NVDA

# Run scheduler (daily at 08:00 UTC)
python main.py schedule --tickers NVDA,AAPL,SPY
```

## Components

| Component | Language | Purpose |
|-----------|----------|---------|
| **TradingAgents** | Python | LLM-powered multi-agent analysis pipeline |
| **mt5-execution-engine** | Rust | Real-time decision watcher, risk manager, MT5 bridge |

---

*Not a developer? Check the [For Non-Technical Users](for-non-technical.md) page.*
