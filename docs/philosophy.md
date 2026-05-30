# Filosofi Jatayu

## Kenapa Jatayu?

```mermaid
flowchart LR
    subgraph Jatayu["🦅 Jatayu — Elang Mitologis"]
        V[👁️ Visi Tajam<br/>Melihat dari ketinggian]
        P[🪽 Sayap Kuat<br/>Terjang badai]
        L[🎯 Ketepatan<br/>Menerkam sasaran]
        K[💪 Kesetiaan<br/>Pantang menyerah]
    end
    
    style Jatayu fill:#fff3e0,stroke:#e65100,color:#000
```

Dalam kisah **Ramayana**, Jatayu adalah seekor **burung elang raksasa** yang setia, pemberani, dan memiliki visi luas dari ketinggian. Meskipun akhirnya gugur, Jatayu berjuang sampai titik darah penghabisan — sebuah simbol **perjuangan tanpa henti**.

## Makna untuk Sistem Ini

| Nilai Jatayu | Makna dalam Sistem | Implementasi |
|-------------|-------------------|--------------|
| **Visi dari Ketinggian** 🦅 | Melihat pasar dari semua sudut | Multi-agent AI menganalisis harga, berita, sentimen, fundamental |
| **Ketepatan** 🎯 | Tidak asal eksekusi | Risk management sebelum tiap trade |
| **Sayap Kuat** 🪽 | Tahan banting | Diversifikasi posisi, stop-loss, manajemen risiko |
| **Kesetiaan** 💪 | Konsisten tiap hari | Scheduler otomatis, 24/7 monitoring |
| **Berjuang Habis-habisan** 🔥 | Optimasi terus | Feedback loop, refleksi, pembelajaran dari kesalahan |

## Filosofi dalam Kode

Setiap bagian dari sistem mencerminkan nilai Jatayu:

```mermaid
flowchart TB
    subgraph Vision["👁️ Visi — Analisis"]
        MA[📈 Market Analyst] -->|Data teknikal| Brain[🧠 AI Core]
        NA[📰 News Analyst] -->|Berita| Brain
        SA[💬 Social Analyst] -->|Sentimen| Brain
        FA[📋 Fundamentals Analyst] -->|Fundamental| Brain
    end
    
    subgraph Precision["🎯 Ketepatan — Eksekusi"]
        Brain --> RM[⚠️ Risk Manager]
        RM -->|Validasi| EX[⚡ Eksekusi]
    end
    
    subgraph Strength["🪽 Kekuatan — Manajemen"]
        EX --> POS[📊 Position Tracking]
        POS --> SL[🛑 Stop Loss]
        POS --> TP[🎯 Take Profit]
    end
    
    subgraph Loyalty["💪 Kesetiaan — Otomasi"]
        POS --> TG[📱 Telegram Notif]
        TG --> SCH[⏰ Scheduler]
        SCH -->|Setiap hari| Brain
    end
    
    style Vision fill:#e3f2fd,stroke:#1565c0,color:#000
    style Precision fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Strength fill:#fff3e0,stroke:#e65100,color:#000
    style Loyalty fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

## Prinsip

1. **Jangan serakah** — Jatayu tahu kapan harus menyerang dan kapan menunggu
2. **Disiplin** — Patuhi aturan risiko, walau keyakinan tinggi
3. **Terus belajar** — Setiap trade adalah pelajaran
4. **Transparan** — Semua keputusan dan eksekusi dikirim ke Telegram, gak ada yang disembunyiin
5. **Otomatis** — Manusia mikir strategi, mesin eksekusi dengan setia

---

> *"Lebih baik mati berjuang daripada hidup dalam ketakutan."*  
> — Semangat Jatayu, yang terbang tinggi dan gugur dengan hormat.
