# Deploy di Windows 10

Panduan lengkap setup JatayuCore di komputer Windows 10 yang nyala 24 jam (kantor, server, dll).

## Pilihan

| Metode | Kesulitan | Kelebihan |
|--------|-----------|-----------|
| **A. WSL2 + systemd** ⭐ | Mudah | Auto-start, logging, restart otomatis |
| **B. WSL2 + nohup** | Mudah | Fallback kalo systemd gak support |
| **C. Python native** | Mudah | Gak perlu WSL, pure Windows |

> **Rekomendasi:** Pilih A. Kalo Windows 10 versi lawas (< 22H2), pilih B.

---

## A. WSL2 + systemd (Rekomendasi)

### 1. Install WSL2

Buka **PowerShell sebagai Administrator**, jalanin:

```powershell
# Install WSL + Ubuntu
wsl --install -d Ubuntu

# Restart komputer pas diminta
# Setelah restart, masukin username & password Ubuntu
```

### 2. Setup JatayuCore di Ubuntu

```bash
# Update package
sudo apt update && sudo apt upgrade -y

# Install uv dan git
sudo apt install -y curl git
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
git clone https://github.com/komelImoet/JatayuCore.git
cd JatayuCore

# Install dependencies
uv sync

# Setup .env
cp .env.example .env
nano .env
# ↑ Paste API key lo (Telegram + DeepSeek + Alpaca)
```

### 3. Setup systemd service

```bash
# Copy service file
sudo cp jatayu.service /etc/systemd/system/jatayu.service

# Edit kalo perlu (interval, tickers)
sudo nano /etc/systemd/system/jatayu.service

# Enable + start
sudo systemctl enable jatayu
sudo systemctl start jatayu

# Cek status
sudo systemctl status jatayu
```

### 4. Auto-start pas Windows boot

Buka **PowerShell sebagai Administrator**, jalanin:

```powershell
.\install-startup.ps1
```

Ini bikin Windows Task yang otomatis start WSL + JatayuCore tiap kali Windows nyala.

**Selesai.** Tinggal restart Windows, bot jalan sendiri.

---

## B. WSL2 + nohup (Fallback)

Kalo systemd gak support (Windows 10 versi lawas):

### 1-2. Sama kaya A (Install WSL + Setup JatayuCore)

### 3. Setup auto-start via .bashrc

```bash
# Di dalam WSL Ubuntu, buka:
nano ~/.bashrc

# Tambah baris ini di paling bawah:
if ! pgrep -f "main.py schedule"; then
    cd ~/JatayuCore && nohup uv run python main.py schedule -D \
        --tickers AAPL,NVDA,MSFT --interval 3 \
        > ~/jatayu.log 2>&1 &
fi
```

### 4. Windows Startup Script

Buat file `C:\Users\...\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\jatayu.bat`:

```batch
@echo off
wsl -d Ubuntu -e bash -c "source ~/.bashrc"
```

Setiap Windows boot → WSL start → bashrc jalan → bot jalan.

---

## C. Python Native (No WSL)

Kalo gak mau WSL sama sekali:

### 1. Install Python

Download [python.org](https://python.org) → Install Python 3.12+  
**Centang "Add Python to PATH"** pas install.

### 2. Clone + Setup

Buka **Command Prompt**:

```cmd
cd C:\
git clone https://github.com/komelImoet/JatayuCore.git
cd JatayuCore
python -m venv .venv
.venv\Scripts\pip install -e .
```

### 3. Buat startup.vbs

Buat file `C:\JatayuCore\startup.vbs`:

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\JatayuCore\.venv\Scripts\python.exe C:\JatayuCore\main.py schedule --tickers AAPL,NVDA,MSFT --interval 3", 0, False
```

### 4. Auto-start

- Tekan `Win + R`, ketik `shell:startup`, Enter
- Copy `startup.vbs` ke folder yang kebuka
- Restart Windows — bot jalan otomatis

---

## Cek Bot Jalan

Setelah setup, tunggu 1 menit terus cek Telegram:
- Harus ada notif "💚 JatayuCore — Scheduler started"

Kalo gak ada:
```bash
# Di WSL
sudo systemctl status jatayu
journalctl -u jatayu --no-pager -n 20

# Atau kalo pake nohup
cat ~/jatayu.log
```

## Matiin / Restart

```bash
# systemd
sudo systemctl stop jatayu
sudo systemctl restart jatayu

# nohup
pkill -f "main.py schedule"
```
