# NULL Security System
# Integrated Cybersecurity Scanner with Real-time Monitoring & AI Analysis

**Sistem keamanan siber terintegrasi untuk deteksi ancaman real-time dengan analisis AI otomatis.**

## 🎯 **Apa Itu NULL Security System?**

NULL adalah sistem keamanan komprehensif yang menggabungkan:
- **🔍 White-box Security Scanner** - 30+ pemeriksaan keamanan sistem
- **🚨 Real-time Attack Detection** - Monitoring serangan blackbox tools 24/7  
- **🤖 AI-powered Analysis** - Analisis otomatis dengan Ollama AI
- **📱 Instant Alerts** - Notifikasi real-time via Telegram

## 🚀 **Quick Start**

### 1. Setup Configuration
```bash
# Copy dan edit file konfigurasi
cp env.example .env
nano .env  # Edit dengan API keys Anda
```

**Required Configuration:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGH...  # Bot Telegram
TELEGRAM_CHAT_ID=123456789                 # Chat ID Telegram  

# AI Configuration - Local Ollama AI (Privacy & Fast)
OLLAMA_MODEL=llama3.2:1b                  # Local AI model (fast & light)
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL
```

### 2. Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run comprehensive security scan
python main_scanner.py

# Atau langsung start monitoring
python start_monitoring.py --continuous
```

## 🔑 **Cara Mendapatkan API Keys**

### Telegram Bot Token & Chat ID:
1. Chat dengan [@BotFather](https://t.me/botfather) di Telegram
2. Ketik `/newbot` dan ikuti instruksi
3. Salin `Bot Token` yang diberikan
4. Chat dengan [@userinfobot](https://t.me/userinfobot) untuk dapat `Chat ID`

### Telegram Bot Token:
1. Chat dengan [@BotFather](https://t.me/botfather) di Telegram
2. Kirim `/newbot` dan ikuti instruksi
3. Salin token yang diberikan

### Chat ID:
1. Chat dengan [@userinfobot](https://t.me/userinfobot)
2. Salin Chat ID yang ditampilkan

### Ollama Setup (Recommended - Local AI):
1. Install Ollama dari [ollama.ai](https://ollama.ai/)
2. Pull model: `ollama pull llama3.2:1b`
3. Start server: `ollama serve`

## 🛡️ **Fitur Utama**

### **Security Assessment (White-box)**
- ✅ **System Information** - OS, kernel, hardware info
- ✅ **Network Security** - Port scanning, service analysis  
- ✅ **User Management** - Account security, permissions
- ✅ **Service Analysis** - SSH, FTP, Web services
- ✅ **System Hardening** - Security modules, configurations
- ✅ **Compliance Checks** - Password policies, audit logs
- ✅ **30+ Security Modules** - Comprehensive coverage

### **Real-time Attack Detection**
- 🚨 **Blackbox Tools Detection** - Subfinder, FFUF, Nuclei, Nmap, dll
- 🚨 **Log Monitoring** - Real-time log file analysis
- 🚨 **Network Monitoring** - Suspicious connection patterns
- 🚨 **Process Monitoring** - Running security tools detection
- 🚨 **Instant Alerts** - Immediate Telegram notifications

### **AI Integration**
- 🤖 **Automated Analysis** - Ollama llama3.2:1b untuk analisis cepat
- 🤖 **Risk Assessment** - Penilaian tingkat risiko otomatis  
- 🤖 **Smart Recommendations** - Saran perbaikan spesifik
- 🤖 **Fast Processing** - Response 10-30 detik (vs 2+ menit)
- 🤖 **Privacy-focused** - AI berjalan local, data tidak ke cloud
- 🤖 **No API Keys** - Tidak perlu API eksternal, fully offline

## 🎮 **Commands Quick Reference**

### **🔍 Main Security Scanning**
```bash
python main_scanner.py              # Full security audit (30+ checks)
python start_monitoring.py --continuous  # 24/7 monitoring mode
```

### **⚡ Individual Security Checks**
```bash
python -m checkers.ssh_checker               # SSH configuration security
python -m checkers.user_group_checker        # User & permissions analysis  
python -m checkers.hardening_checker         # System hardening status
python -m checkers.web_checker               # Web services security
python -m core.port_scanner         # Open ports scanning
```

### **🚨 Monitoring Modes**
```bash
python start_monitoring.py --continuous    # Continuous monitoring
python start_monitoring.py --single        # Single scan
python start_monitoring.py --interval 30   # Custom interval (seconds)
python start_monitoring.py --verbose       # Detailed logging
```

### **🤖 AI & Configuration**
```bash
ollama serve                        # Start Ollama AI server
ollama pull llama3.2:1b            # Download AI model (1.3GB - fast!)
copy env.example .env               # Setup configuration
```

📖 **Detailed Commands:** See [COMMANDS_GUIDE.md](docs/COMMANDS_GUIDE.md) for complete command reference

## 📋 **Cara Penggunaan**

### **Mode 1: Comprehensive Scan + Monitoring**
```bash
python main_scanner.py
# Setelah scan selesai, pilih 'y' untuk continuous monitoring
```

### **Mode 2: Direct Continuous Monitoring**  
```bash
python start_monitoring.py --continuous
# Monitoring real-time tanpa scan awal
```

### **Mode 3: Quick Security Check**
```bash
python start_monitoring.py --scan  
# Scan cepat untuk deteksi serangan saat ini
```

## 🎯 **Blackbox Tools yang Terdeteksi**

| **Category** | **Tools** |
|--------------|-----------|
| **Subdomain Enum** | Subfinder, Amass, TheHarvester |
| **Web Fuzzing** | FFUF, Gobuster, Dirb, Wfuzz |  
| **Vulnerability Scan** | Nuclei, Nikto, SQLMap |
| **Network Scan** | Nmap, Masscan, Zmap |
| **Web Crawling** | Katana, ParamSpider, Arjun |

## 🔬 **Example Output**

### **Security Scan Results:**
```
--- Pemeriksaan Informasi Sistem & Konfigurasi Umum ---
[+] OS: Linux Ubuntu 20.04.6 LTS
[+] Kernel: 5.4.0-182-generic
[+] Architecture: x86_64
[!] WARNING: 5 critical security issues found
[*] Running AI analysis...
[+] Telegram report sent successfully
```

### **Real-time Attack Detection:**
```
🚨 SERANGAN TERDETEKSI! [2025-08-31 15:30:45]
Tool: subfinder
Source: log  
Details: GET /api/users HTTP/1.1 User-Agent: subfinder/2.6.3

🔍 Melakukan analisis otomatis...
🤖 Mendapatkan analisis AI...
📱 Mengirim notifikasi darurat...
✅ Analisis dan notifikasi selesai!
🛡️ Continuing monitoring...
```

## 📁 **File Structure**

```
null/
├── core/                     # Core scanner utilities
│   ├── host_utils.py
│   ├── port_scanner.py
│   └── root_checks.py
├── analysis/
│   └── log_analyzer.py
├── monitoring/
│   └── security_monitor.py
├── tools/
│   └── emergency_ubuntu_fix.py
├── checkers/                 # 25+ security modules
├── backup/
├── scripts/
├── docs/
├── main_scanner.py
├── start_monitoring.py
├── cli_menu.py
├── launcher.py
├── utils.py
├── requirements.txt
├── env.example
└── .env
```

## 🎓 **Untuk Proposal Skripsi**

**Lihat file:** `docs/Dokumentasi Projek.md` untuk dokumentasi lengkap meliputi:
- 📋 Deskripsi proyek komprehensif
- 🏗️ Arsitektur sistem  
- 🔬 Metodologi penelitian
- 📈 Hasil & pencapaian
- 📝 Template proposal skripsi

## 🤝 **Contributing**

Proyek ini dikembangkan untuk tujuan akademis (skripsi). Kontribusi dan saran sangat diterima!

## 📄 **License**

Academic Project - Developed for thesis research purposes.

---

**🛡️ NULL Security System - Protecting your infrastructure with intelligent automation**
3. Klik "Create API Key" 
4. Salin API key yang dibuat

## ✨ Features

- **🔍 Security Audit**: Komprehensif server security checks
- **🛡️ Attack Detection**: Deteksi real-time serangan dari Subfinder, Katana, FFUF, Nuclei, Nmap, ParamSpider
- **🤖 AI Analysis**: Analisis mendalam dengan Ollama AI
- **📱 Telegram Alerts**: Notifikasi real-time ke Telegram

## 🧪 Testing

```bash
python3 attack_simulator.py  # Test attack detection
```

## 📋 Requirements

- Python 3.7+
- Linux/Windows
- Root access (optional, untuk hasil optimal)


