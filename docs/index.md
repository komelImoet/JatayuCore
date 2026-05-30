# JatayuCore

**Multi-Agent AI Trading Framework** — Terinspirasi dari Jatayu, elang mitologis yang memiliki visi tajam, ketepatan, dan kesetiaan.

```mermaid
flowchart TB
    subgraph Jatayu["🦅 JatayuCore"]
        direction TB
        V[👁️ Visi Tajam<br/>Multi-Agent AI] --> P[🎯 Ketepatan<br/>Risk Management]
        P --> K[🪽 Kekuatan<br/>Eksekusi Otomatis]
        K --> S[💪 Kesetiaan<br/>Telegram Setiap Saat]
    end
    
    style Jatayu fill:#fff3e0,stroke:#e65100,color:#000
```

## Pipeline

```mermaid
flowchart LR
    subgraph Python["🐍 JatayuCore (Python)"]
        TA[Jatayu Agent Pipeline<br/>Analis → Debat → Eksekusi]
    end
    
    subgraph Storage["💾 Storage"]
        JS[(JSON State Logs)]
    end
    
    subgraph Telegram["📱 Telegram"]
        TG[Bot Notifications<br/>Signal + Eksekusi + Error]
    end
    
    TA -->|Simpan| JS
    TA -->|Kirim| TG
    JS -->|Baca| RE[Rust Engine]
    RE -->|Execute| MT[MT5 / Alpaca]
    RE -->|Kirim| TG
    
    style Python fill:#e3f2fd,stroke:#1565c0,color:#000
    style Storage fill:#f5f5f5,stroke:#616161,color:#000
    style Telegram fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

## Filosofi Singkat

Jatayu dalam kisah Ramayana adalah elang raksasa yang:
- **Terbang tinggi** — melihat luas, tidak terjebak detail sempit
- **Menyambar tepat** — tidak asal serang, ada kalkulasi
- **Setia & gigih** — berjuang sampai akhir

Sama seperti sistem ini: AI menganalisis dari semua sudut, risk manager memvalidasi, eksekusi otomatis, dan lo tinggal terima laporan di Telegram.

## Fitur

- **Multi-Agent AI** — 7 agen spesialis menganalisis pasar dari berbagai sudut
- **Auto Eksekusi** — Order otomatis ke MT5 atau Alpaca
- **Telegram Alert** — Real-time dari analysis sampe eksekusi
- **Scheduler Harian** — Jalan otomatis tiap hari
- **Risk Management** — Stop loss, exposure limit, rating filter
- **Docker Siap** — Deploy pake `docker compose up`

## Start Cepat

```bash
git clone https://github.com/komelImoet/JatayuCore.git
cd JatayuCore

# Set Telegram
export TELEGRAM_BOT_TOKEN="token_lo"
export TELEGRAM_CHAT_ID="chat_id_lo"

# Analisis saham
python main.py run AAPL

# Scheduler otomatis tiap hari
python main.py schedule --tickers AAPL,NVDA,MSFT
```

---

*"Terbang tinggi, sambar tepat, pantang menyerah."* — JatayuCore
