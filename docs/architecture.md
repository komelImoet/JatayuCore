# Architecture

## System Design

```mermaid
flowchart TB
    subgraph Scheduler["⏰ Scheduler (Python)"]
        S[Daily Cron<br/>08:00 UTC]
    end
    
    subgraph TA["🐍 TradingAgents (Python)"]
        direction TB
        A1[Market Analyst] --> AD[Agent Debate]
        A2[News Analyst] --> AD
        A3[Social Analyst] --> AD
        A4[Fundamentals Analyst] --> AD
        AD --> RMG[Risk Management<br/>Conservative / Neutral / Aggressive]
        RMG --> TR[Trader Agent]
        TR --> PM[Portfolio Manager]
    end
    
    subgraph Storage["💾 Storage"]
        JS[(JSON State Logs<br/>~/.tradingagents/logs)]
    end
    
    subgraph Engine["🦀 Execution Engine (Rust)"]
        direction TB
        W[File Watcher<br/>inotify] --> P[Parser]
        P --> RK[Risk Manager<br/>Rating / Exposure / Duplicate]
        RK --> OM[Order Manager]
        OM --> C[MT5 Connector<br/>JSON-RPC]
    end
    
    subgraph Sidecar["🐍 Python Sidecar"]
        SC[mt5_sidecar.py<br/>MetaTrader5 Library]
    end
    
    subgraph MT5["💹 MetaTrader 5 (Windows)"]
        MT[MT5 Terminal]
        EA[MQL EA<br/>Telegram Sender]
    end
    
    subgraph TG["📱 Telegram"]
        CHAT[Your Telegram]
    end
    
    S -->|Trigger daily| TA
    TA -->|Write JSON| JS
    JS -->|Notify| W
    C -->|JSON-RPC stdin/stdout| SC
    SC -->|mt5 API| MT
    MT -->|Execution result| EA
    EA -->|Send message| CHAT
    TA -.->|Analysis signal| CHAT
    Engine -.->|Execution events| CHAT
    
    style TA fill:#e3f2fd,stroke:#1565c0,color:#000
    style Engine fill:#fff3e0,stroke:#e65100,color:#000
    style Sidecar fill:#fce4ec,stroke:#c62828,color:#000
    style MT5 fill:#e8f5e9,stroke:#2e7d32,color:#000
    style TG fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style Storage fill:#f5f5f5,stroke:#616161,color:#000
    style Scheduler fill:#e0f7fa,stroke:#00838f,color:#000
```

## Agent Interaction Flow

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant TA as TradingAgents
    participant A as AI Agents
    participant JS as JSON Log
    participant E as Rust Engine
    participant MT as MT5
    participant TG as Telegram

    S->>TA: Start daily analysis
    
    par Analyst Phase
        A->>A: Market Analyst - price data
        A->>A: News Analyst - news feed
        A->>A: Social Analyst - sentiment
        A->>A: Fundamentals Analyst - financials
    end
    
    A->>A: Bull/Bear Research Debate
    A->>A: Risk Management Discussion
    A->>A: Trader - transaction proposal
    A->>A: Portfolio Manager - final rating
    
    TA->>JS: Write decision JSON
    
    Note over E: File watcher detects new JSON
    
    E->>JS: Read decision file
    E->>E: Parse structured data
    E->>E: Risk validation
    
    alt Risk Approved
        E->>MT: Send order (JSON-RPC)
        MT-->>E: Order filled
        E->>TG: ✅ Order executed notification
    else Risk Rejected
        E->>TG: ❌ Risk rejected notification
    end
    
    TA->>TG: 📊 Analysis signal card
    
    loop Every hour
        E->>MT: Sync positions
        E->>TG: 📋 Position summary
    end
```

## Component Details

### Python Layer (TradingAgents)

The Python framework uses **LangGraph** to orchestrate a directed acyclic graph of agent nodes. Each agent is an LLM-powered node with access to specific tools (data vendors, analysis functions).

**Agents:**

| Agent | Role | Tools |
|-------|------|-------|
| Market Analyst | Technical indicators, price action | yfinance, stockstats |
| News Analyst | Latest news sentiment | yfinance news |
| Social Analyst | Social sentiment analysis | yfinance |
| Fundamentals Analyst | Financial statements | yfinance |
| Bull Researcher | Makes investment case | Analyst reports |
| Bear Researcher | Makes against case | Analyst reports |
| Risk Managers | Conservative/Neutral/Aggressive | Portfolio data |
| Trader | Transaction proposal | Research plan |
| Portfolio Manager | Final rating & execution plan | All reports |

**Output:** JSON state files written to `~/.tradingagents/logs/<TICKER>/TradingAgentsStrategy_logs/full_states_log_<DATE>.json`

### Rust Layer (mt5-execution-engine)

The Rust engine is a high-performance, real-time execution bridge:

```mermaid
flowchart LR
    subgraph Engine["🦀 mt5-execution-engine"]
        W[📁 File Watcher] --> PP[📝 Parser]
        PP --> RK[⚠️ Risk Manager]
        RK --> OM[📋 Order Manager]
        OM --> CN[🔌 MT5 Connector]
        OM --> PT[📊 Position Tracker]
        CN --> TB[📱 Telegram Bot]
        PT --> TB
        RK --> TB
    end
    
    style Engine fill:#fff3e0,stroke:#e65100,color:#000
```

**Event Flow:**

| Step | Component | Action | Telegram? |
|------|-----------|--------|-----------|
| 1 | Watcher | Detects new JSON file | — |
| 2 | Parser | Extracts rating, prices, sizing | — |
| 3 | Risk Manager | Validates decision | ✅ Yes |
| 4 | Order Manager | Creates order record | — |
| 5 | Connector | Sends to MT5 via JSON-RPC | — |
| 6 | Connector | Returns fill result | ✅ Yes |
| 7 | Position Tracker | Updates positions | ✅ Hourly |

## Data Flow

1. **Scheduler** triggers daily analysis at configured time (default: 08:00 UTC)
2. **TradingAgents** runs the pipeline for each ticker in the watchlist
3. **JSON state** is written to shared volume
4. **Rust engine** detects new file via `inotify`
5. **Risk validation** checks rating threshold, exposure limits, duplicate prevention
6. **Order execution** via JSON-RPC to MT5 Python sidecar
7. **Telegram notifications** at every stage from both Python and Rust layers
