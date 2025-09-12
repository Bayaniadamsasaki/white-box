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

# AI Configuration (Choose one)
USE_OLLAMA=true                            # Use local Ollama AI
OLLAMA_MODEL=deepseek-r1:8b               # Local AI model
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL

# OR use cloud AI (optional)
GEMINI_API_KEY=AIza...                     # Google Gemini API (if USE_OLLAMA=false)
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
2. Pull model: `ollama pull deepseek-r1:8b`
3. Start server: `ollama serve`
4. Test: `python test_ollama.py`

### Gemini API Key (Optional - Cloud AI):
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan akun Google
3. Klik "Create API Key"
4. Set `USE_OLLAMA=false` di .env
5. Salin API key yang dihasilkan

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
- 🤖 **Automated Analysis** - Ollama Local AI untuk analisis hasil
- 🤖 **Risk Assessment** - Penilaian tingkat risiko otomatis
- 🤖 **Smart Recommendations** - Saran perbaikan spesifik
- 🤖 **Context-aware** - Analisis berdasarkan konteks sistem
- 🤖 **Privacy-focused** - AI berjalan local, data tidak ke cloud

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
├── 📂 Core Scanner (White-box Security)
│   ├── main_scanner.py              # Main orchestrator
│   ├── system_info_checker.py       # System analysis
│   ├── network_config_checker.py    # Network security
│   ├── ssh_checker.py              # SSH analysis
│   └── [25+ security modules]       # Specialized checks
│
├── 📂 Real-time Monitoring  
│   ├── security_monitor.py          # Monitoring engine
│   ├── start_monitoring.py          # Easy launcher
│   └── attack_simulator.py          # Testing tools
│
├── 📂 AI & Communications
│   ├── utils.py                     # Gemini + Telegram
│   └── security_config.py          # Configuration
│
└── 📂 Documentation
    ├── README.md                    # This file
    ├── Dokumentasi Projek.md        # Complete project docs
    └── MONITORING_GUIDE.md         # Monitoring guide
```

## 🎓 **Untuk Proposal Skripsi**

**Lihat file:** `Dokumentasi Projek.md` untuk dokumentasi lengkap meliputi:
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
- **🤖 AI Analysis**: Analisis mendalam dengan Gemini AI
- **📱 Telegram Alerts**: Notifikasi real-time ke Telegram

## 🧪 Testing

```bash
python3 attack_simulator.py  # Test attack detection
```

## 📋 Requirements

- Python 3.7+
- Linux/Windows
- Root access (optional, untuk hasil optimal)
