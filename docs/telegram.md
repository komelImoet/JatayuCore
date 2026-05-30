# Telegram Notifications

JatayuCore sends real-time Telegram notifications at every stage of the trading pipeline.

## How Notifications Flow

```mermaid
flowchart TB
    subgraph PythonLayer["🐍 JatayuCore (Python)"]
        A[Analysis Complete] -->|send_decision| TG1[📱 Analysis Signal]
        E[Error Occurs] -->|send_error| TG2[📱 Error Alert]
    end
    
    subgraph RustLayer["🦀 Execution Engine (Rust)"]
        D[Decision Received] -->|send_decision| TG3[📱 Decision Card]
        RK[Risk Check] -->|send_risk_decision| TG4{Approved?}
        TG4 -->|Yes| TG5[📱 ✅ Risk PASSED]
        TG4 -->|No| TG6[📱 ❌ Risk REJECTED]
        OF[Order Filled] -->|send_order_filled| TG7[📱 📈 Order FILLED]
        OFAIL[Order Failed] -->|send_order_failed| TG8[📱 ⚠️ Order FAILED]
        PS[Position Sync] -->|send_position_summary| TG9[📱 📊 Position Summary]
        HC[Health Check] -->|send_health| TG10[📱 💚 Engine Status]
        ERR[Engine Error] -->|send_error| TG11[📱 🚨 Error Alert]
    end
    
    style PythonLayer fill:#e3f2fd,stroke:#1565c0,color:#000
    style RustLayer fill:#fff3e0,stroke:#e65100,color:#000
```

## Notification Types

### Python Layer — Analysis Signal

When JatayuCore completes an analysis, you receive a detailed signal card:

```
🤖 JatayuCore Signal
━━━━━━━━━━━━━━━━━━
🟢 Rating: Buy
Ticker: NVDA
Date: 2024-05-10
Action: Buy
Entry: 124.50
Stop Loss: 118.27
Price Target: 150.00
Sizing: 5% of portfolio
Horizon: 3-6 months

Summary:
Buy NVDA at market with 5% position size.
Set stop-loss at $118.27 (-5%) and take-profit at $150.00 (+20%).

Thesis:
NVDA shows strong momentum with...
```

### Rust Layer — Execution Events

```mermaid
flowchart LR
    subgraph TG["📱 Telegram Messages"]
        M1["✅ Risk Check PASSED<br/>Ticker: NVDA"]
        M2["❌ Risk Check REJECTED<br/>Ticker: AAPL<br/>Reason: Duplicate position"]
        M3["📈 Order FILLED<br/>Ticket: #12345<br/>Fill: $124.50"]
        M4["⚠️ Order FAILED<br/>Error: Insufficient margin"]
        M5["📊 Position Summary<br/>2 positions | $12.5K"]
        M6["💚 Engine reconnected"]
        M7["🚨 Connection lost"]
    end
    
    style TG fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

**Risk Approved:**
```
✅ Risk Check PASSED
━━━━━━━━━━━━━━━━━━
Ticker: NVDA
```

**Risk Rejected:**
```
❌ Risk Check REJECTED
━━━━━━━━━━━━━━━━━━
Ticker: AAPL
Reason: Position already open for AAPL
```

**Order Filled:**
```
📈 Order FILLED
━━━━━━━━━━━━━━━━━━
Ticker: NVDA
Direction: Buy
Ticket: #12345678
Fill Price: 124.48
```

**Order Failed:**
```
⚠️ Order FAILED
━━━━━━━━━━━━━━━━━━
Ticker: NVDA
Error: Insufficient margin
```

### Status & Health

**Position Summary (every hour):**
```
📊 Position Summary
━━━━━━━━━━━━━━━━━━
Open Positions: 2
Equity: 12500.00
Balance: 10000.00
Exposure: 2500.00
```

**Health Alert:**
```
💚 Engine Health
━━━━━━━━━━━━━━━━━━
Status: MT5 reconnected
```

## Configuration

Set in `.env`:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmNOPqrstUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Bot Token Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy the token
4. Find your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

## Disabling Notifications

Leave `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` empty in `.env` to disable all Telegram notifications.
