# Architecture

## System Design

```mermaid
flowchart TB
    subgraph Scheduler["⏰ Scheduler"]
        S[Weekday? 08:00 UTC]
    end

    subgraph JatayuCore["🐍 JatayuCore (Python)"]
        direction TB
        A1[Market Analyst] --> AD[Agent Debate]
        A2[News Analyst] --> AD
        A3[Social Analyst] --> AD
        A4[Fundamentals Analyst] --> AD
        AD --> RMG[Risk Management]
        RMG --> PM[Portfolio Manager]
        PM --> SIG{Final Rating}
    end

    subgraph Alpaca["💹 Alpaca Broker"]
        BUY[Buy Market Order]
        SELL[Close Position]
        SKIP[Skip / Hold]
    end

    subgraph Monitor["📡 PositionMonitor (Thread)"]
        SL[Stop Loss Check /60s]
        SUM[Position Summary /3600s]
        HB[Heartbeat /7200s]
        PNL[Daily P&L]
    end

    subgraph Storage["💾 Storage"]
        JS[(JSON State Logs)]
    end

    subgraph TG["📱 Telegram"]
        CHAT[Your Telegram]
    end

    S -->|Trigger| JatayuCore
    JatayuCore -->|Write| JS

    SIG -->|Buy/Overweight| BUY
    SIG -->|Sell/Underweight| SELL
    SIG -->|Hold| SKIP

    BUY --> TG
    SELL --> TG
    SKIP --> TG

    Monitor --> SL -->|Hit| BUY
    Monitor --> SUM --> TG
    Monitor --> HB --> TG
    Monitor --> PNL --> TG

    JatayuCore -.->|Signal card| TG

    style JatayuCore fill:#e3f2fd,stroke:#1565c0,color:#000
    style Alpaca fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Monitor fill:#fff3e0,stroke:#e65100,color:#000
    style TG fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style Scheduler fill:#e0f7fa,stroke:#00838f,color:#000
    style Storage fill:#f5f5f5,stroke:#616161,color:#000
```

## Agent Flow

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant TA as JatayuCore
    participant A as AI Agents
    participant B as Alpaca
    participant M as Monitor
    participant TG as Telegram

    S->>TA: Start daily analysis

    par Analyst Phase
        A->>A: Market Analyst
        A->>A: News Analyst
        A->>A: Social Analyst
        A->>A: Fundamentals Analyst
    end

    A->>A: Bull/Bear Debate
    A->>A: Risk Management
    A->>A: Portfolio Manager → Rating

    TA->>TG: 📊 Signal card

    alt Buy/Overweight
        TA->>B: Check dup position
        B-->>TA: OK
        TA->>B: Place market order
        B-->>TA: Order #123
        TA->>TG: 🟢 Order Placed
    else Sell/Underweight
        TA->>B: Close position
        B-->>TA: Closed
        TA->>TG: 🔴 Position Closed
    end

    Note over M: Background thread
    loop Every 60s
        M->>B: Check SL
        B-->>M: Price data
        alt SL hit
            M->>B: Close position
            M->>TG: 🚨 Stop Loss Triggered
        end
    end

    loop Every 1h
        M->>B: Get positions
        M->>TG: 📊 Position Summary
    end

    loop Every 2h
        M->>TG: 💚 Heartbeat
    end

    Note over M: Daily at first run
    M->>TG: 💰 Daily P&L Report
```

## Components

### JatayuCore (Python)
| Agent | Role |
|-------|------|
| Market Analyst | Technical indicators, price action |
| News Analyst | Latest news sentiment |
| Social Analyst | Social sentiment analysis |
| Fundamentals Analyst | Financial statements |
| Bull/Bear Researchers | Structured debate |
| Risk Managers | Conservative/Neutral/Aggressive |
| Portfolio Manager | Final rating & execution plan |

### Alpaca Broker (`tradingagents/brokers/alpaca_broker.py`)
| Feature | Detail |
|---------|--------|
| Paper/Live | Configurable via constructor |
| Buy Execution | Market order, qty from % equity |
| Sell Execution | Close existing position |
| Duplicate Guard | Skip Buy if position exists |
| Sizing | % equity → shares, fallback 1% |
| Telegram Notif | Order placed/failed sent via notifier |

### PositionMonitor (`tradingagents/monitor.py`)
| Check | Interval | Action |
|-------|----------|--------|
| Stop Loss | 60s | Auto close + Telegram alert |
| Position Summary | 1h | P&L per position |
| Heartbeat | 2h | "Still alive" + equity |
| Daily P&L | Once/day | Equity, cash, buying power |

## Data Flow

1. **Scheduler** checks market hours → triggers analysis
2. **JatayuCore** runs agent pipeline for each ticker
3. **Signal** extracted (Buy/Overweight/Hold/Sell/Underweight)
4. **Alpaca** executes if signal is actionable
5. **Telegram** notified at every stage
6. **PositionMonitor** runs in background daemon thread
