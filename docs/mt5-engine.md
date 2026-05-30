# MT5 Execution Engine

The `mt5-execution-engine` is a high-performance Rust bridge that monitors JatayuCore's JSON output and executes trades in MetaTrader 5.

## Architecture

```mermaid
flowchart TB
    subgraph Engine["🦀 mt5-execution-engine"]
        direction TB
        W[📁 File Watcher<br/>inotify/kqueue] --> P[📝 Parser<br/>Regex Extraction]
        P --> RK[⚠️ Risk Manager<br/>Rating / Exposure / Duplicate / SL]
        RK --> OM[📋 Order Manager<br/>Lifecycle Tracking]
        OM --> CN[🔌 MT5 Connector<br/>JSON-RPC Client]
        
        PT[📊 Position Tracker<br/>Periodic Sync] --> TG[📱 Telegram Bot]
        CN --> TG
        OM --> TG
        RK --> TG
    end
    
    subgraph Sidecar["🐍 Python Sidecar"]
        SC[mt5_sidecar.py<br/>JSON-RPC Server]
        SC --> MT5Lib[MetaTrader5<br/>Python Library]
    end
    
    subgraph Terminal["💹 MetaTrader 5"]
        MT[MT5 Terminal]
    end
    
    CN -->|stdin/stdout<br/>JSON-RPC| SC
    MT5Lib -->|mt5 API| MT
    
    style Engine fill:#fff3e0,stroke:#e65100,color:#000
    style Sidecar fill:#fce4ec,stroke:#c62828,color:#000
    style Terminal fill:#e8f5e9,stroke:#2e7d32,color:#000
```

## How It Works

```mermaid
sequenceDiagram
    participant FS as File System
    participant W as Watcher
    participant P as Parser
    participant RK as Risk Manager
    participant OM as Order Manager
    participant CN as Connector
    participant MT as MT5
    participant TG as Telegram
    
    FS-->>W: New JSON file detected
    W->>P: Read & parse file
    P->>RK: Structured decision
    
    RK->>RK: Validate rating
    RK->>RK: Check exposure
    RK->>RK: Prevent duplicates
    
    alt Approved
        RK->>TG: ✅ Risk PASSED
        RK->>OM: Create order
        OM->>CN: Send order
        CN->>MT: JSON-RPC: send_order
        
        alt Success
            MT-->>CN: {ticket, fill_price}
            CN->>OM: Mark filled
            CN->>TG: 📈 Order FILLED
        else Failure
            MT-->>CN: {error}
            CN->>OM: Mark rejected
            CN->>TG: ⚠️ Order FAILED
        end
    else Rejected
        RK->>TG: ❌ Risk REJECTED
    end
    
    loop Every 5 seconds
        CN->>MT: get_positions
        MT-->>CN: Position list
        CN->>PT: Sync positions
    end
    
    loop Every 1 hour
        PT->>TG: 📊 Position Summary
    end
```

## CLI Options

```bash
# Run with default config
mt5-execution-engine

# Run with custom config
mt5-execution-engine --config /path/to/config.toml

# Dry-run mode (validate but don't execute)
mt5-execution-engine --dry-run
```

## Risk Rules

```mermaid
flowchart LR
    subgraph Input["📥 Decision Input"]
        R[Rating: Buy/Sell] 
        E[Entry Price]
        SL[Stop Loss]
        S[Sizing %]
    end
    
    subgraph Checks["⚠️ Risk Checks"]
        C1{Rating ≥<br/>Minimum?}
        C2{Already have<br/>position?}
        C3{Stop Loss<br/>provided?}
        C4{Exposure<br/>within limit?}
    end
    
    subgraph Result["✅ / ❌"]
        OK[Approved]
        NO[Rejected]
    end
    
    Input --> C1
    C1 -->|Yes| C2
    C1 -->|No| NO
    C2 -->|No| C3
    C2 -->|Yes| NO
    C3 -->|Yes| C4
    C3 -->|No| C4
    C4 -->|Yes| OK
    C4 -->|No| NO
    
    style Input fill:#e3f2fd
    style Checks fill:#fff3e0
    style Result fill:#e8f5e9
```

### Risk Configuration

| Rule | Config Key | Default | Description |
|------|-----------|---------|-------------|
| Minimum Rating | `risk.min_rating` | Hold | Skip ratings below this |
| Max Position | `risk.max_position_pct` | 10% | Max % of equity per position |
| Max Exposure | `risk.max_total_exposure_pct` | 50% | Max % across all positions |
| Require Stop Loss | `risk.require_stop_loss` | true | Reject if no SL provided |
| Default Stop Loss | `risk.default_stop_loss_pct` | 5% | Fallback SL % from entry |
| Max Slippage | `execution.max_slippage_pct` | 0.5% | Max allowed price deviation |
| Retry Attempts | `execution.retry_attempts` | 3 | Retry failed orders |

## Telegram Notifications

The engine sends these real-time alerts:

```mermaid
flowchart TB
    subgraph Events["🚀 Engine Events"]
        D[📝 Decision Received]
        RA[✅ Risk Approved]
        RR[❌ Risk Rejected]
        OF[📈 Order Filled]
        OFAIL[⚠️ Order Failed]
        PS[📊 Position Summary]
        HC[💚 Health Check]
        ERR[🚨 Error]
    end
    
    subgraph TG["📱 Telegram Chat"]
        M1["🤖 Decision: NVDA Buy"]
        M2["✅ Risk PASSED"]
        M3["❌ Risk REJECTED: Duplicate"]
        M4["📈 Filled #12345 @ $124.50"]
        M5["⚠️ Failed: Insufficient margin"]
        M6["📊 2 positions | $12.5K equity"]
        M7["💚 Engine reconnected"]
        M8["🚨 MT5 connection lost"]
    end
    
    D --> M1
    RA --> M2
    RR --> M3
    OF --> M4
    OFAIL --> M5
    PS --> M6
    HC --> M7
    ERR --> M8
    
    style Events fill:#e3f2fd
    style TG fill:#f3e5f5
```

## Sidecar

The Python sidecar (`sidecar/mt5_sidecar.py`) handles the actual MT5 interaction:

| Method | Description |
|--------|-------------|
| `connect` | Initialize MT5 terminal connection |
| `send_order` | Place market/limit orders |
| `get_positions` | Fetch open positions |
| `get_account_info` | Fetch equity and balance |
| `close_position` | Close positions by ticket |
| `ping` | Health check |
| `shutdown` | Clean shutdown |

## Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Decision received
    Pending --> Submitted: Risk approved
    Submitted --> Filled: MT5 confirmed
    Submitted --> Partial: Partially filled
    Submitted --> Rejected: MT5 error
    Filled --> Closed: Position closed
    Partial --> Filled: Remaining filled
    Partial --> Rejected: Canceled
    Rejected --> [*]
    Closed --> [*]
```
