# 🚀 NULL Security System - Panduan Perintah

## 📋 **PERINTAH UTAMA**

### 1. **🔍 Security Scanning (White-box)**
```bash
# Jalankan pemindaian keamanan komprehensif (30+ checks)
python main_scanner.py

# Jalankan checker individual 
python ssh_checker.py           # Cek konfigurasi SSH
python user_group_checker.py    # Cek user & group security
python hardening_checker.py     # Cek system hardening
python web_checker.py           # Cek web services security
python port_scanner.py          # Scan port yang terbuka
```

### 2. **🚨 Real-time Monitoring (Blackbox Detection)**
```bash
# Start monitoring berkelanjutan (recommended)
python start_monitoring.py --continuous

# Monitoring mode lain
python start_monitoring.py --single      # Single scan
python start_monitoring.py --interval 30 # Custom interval (detik)
python start_monitoring.py --verbose     # Detail logging
```

### 3. **🤖 AI Analysis Setup & Testing**
```bash
# Setup Ollama AI (Local - Free & Private)
ollama serve                    # Start Ollama server
ollama pull llama3.2:1b        # Download AI model (1.3GB - fast!)
ollama list                    # Check installed models

# Test AI connection
python -c "from utils import get_ai_suggestion; print('AI Ready!')"
```

---

## ⚙️ **KONFIGURASI AWAL**

### 1. **Setup Environment**
```bash
# Copy dan edit konfigurasi
copy env.example .env
notepad .env    # Windows
# atau
nano .env       # Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. **Telegram Bot Setup** (Required)
1. Chat dengan [@BotFather](https://t.me/botfather) di Telegram
2. Buat bot baru: `/newbot`
3. Copy token ke `TELEGRAM_BOT_TOKEN` di `.env`
4. Chat dengan [@userinfobot](https://t.me/userinfobot) untuk dapatkan Chat ID
5. Copy Chat ID ke `TELEGRAM_CHAT_ID` di `.env`

### 3. **Ollama AI Setup** (Recommended)
```bash
# Download & install Ollama
# Windows: https://ollama.ai/download/windows
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Start server & download model
ollama serve
ollama pull llama3.2:1b
```

---

## 🎯 **SCENARIOS & USE CASES**

### **Scenario 1: Quick Security Check**
```bash
# Cek SSH security saja
python ssh_checker.py

# Cek user permissions
python user_group_checker.py

# Cek port terbuka
python port_scanner.py
```

### **Scenario 2: Comprehensive Security Audit**
```bash
# Full system security scan
python main_scanner.py

# Hasil akan dikirim ke Telegram dengan AI analysis
```

### **Scenario 3: Red Team vs Blue Team Testing**
```bash
# Terminal 1: Start monitoring
python start_monitoring.py --continuous

# Terminal 2: Jalankan attack tools (untuk testing)
nmap -sS target.com
ffuf -u http://target/FUZZ -w wordlist.txt
nuclei -u http://target

# Monitor akan detect dan analisis otomatis
```

### **Scenario 4: Server Deployment**
```bash
# Linux deployment
bash deploy_ubuntu.sh

# Manual setup
python main_scanner.py          # Initial security check
python start_monitoring.py --continuous &  # Background monitoring
```

---

## 🔧 **TROUBLESHOOTING COMMANDS**

### **Check System Status**
```bash
# Check Python dependencies
pip list | grep -E "(requests|psutil|python-dotenv)"

# Check Ollama status
curl http://localhost:11434/api/tags  # Should return model list

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Telegram:', bool(os.getenv('TELEGRAM_BOT_TOKEN'))); print('AI Model:', os.getenv('OLLAMA_MODEL'))"

# Test Telegram connection
python -c "from utils import send_to_telegram; send_to_telegram('Test', 'System OK', 'Connection test successful')"
```

### **Debug Mode Commands**
```bash
# Verbose monitoring dengan debug info
python start_monitoring.py --continuous --verbose

# Check individual modules
python utils.py  # Test utilities
python security_monitor.py  # Test monitoring engine
```

### **Performance Monitoring**
```bash
# Monitor resource usage saat scanning
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"

# Check log files
dir *.log      # Windows
ls -la *.log   # Linux
```

---

## 📊 **REAL-TIME MONITORING COMMANDS**

### **Start Different Monitoring Modes**
```bash
# Continuous monitoring (recommended for servers)
python start_monitoring.py --continuous

# Interval-based monitoring 
python start_monitoring.py --interval 60  # Check every 60 seconds

# Single shot monitoring
python start_monitoring.py --single

# Background monitoring (Linux)
nohup python start_monitoring.py --continuous > monitor.log 2>&1 &
```

### **Monitor Specific Threats**
```bash
# Monitor with focus on specific attack types
python security_monitor.py  # Direct monitoring script

# Check what's being monitored
python -c "from security_monitor import SecurityEvent; print('Monitoring ready')"
```

---

## 🎪 **DEMO & TESTING COMMANDS**

### **Test Security Detection**
```bash
# Test dengan tools yang aman (jika tersedia)
ping localhost                    # Basic connectivity
nslookup google.com               # DNS lookup
curl -I http://httpbin.org/ip     # HTTP request
```

### **Simulate Log Entries** (Untuk Testing)
```bash
# Buat log entry manual untuk testing detection
echo "$(date) - Test log entry from FFUF scan" >> test_security.log
echo "$(date) - Subfinder scanning started" >> test_security.log

# Monitor akan detect aktivitas ini
```

---

## 🎁 **BONUS COMMANDS**

### **System Health Check**
```bash
# Quick system overview
python system_info_checker.py

# Network configuration check
python network_config_checker.py

# Environment security check
python environment_checker.py
```

### **Generate Reports**
```bash
# Full security report (akan dikirim ke Telegram)
python main_scanner.py > security_report_$(date +%Y%m%d).txt

# Individual module reports
python ssh_checker.py > ssh_report.txt
python hardening_checker.py > hardening_report.txt
```

### **Maintenance Commands**
```bash
# Update AI model
ollama pull llama3.2:1b

# Clean logs
del *.log      # Windows
rm *.log       # Linux

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

## 🏁 **QUICK START WORKFLOW**

```bash
# 1. Setup konfigurasi
copy env.example .env
notepad .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Ollama
ollama serve
ollama pull llama3.2:1b

# 4. Test system
python ssh_checker.py

# 5. Start full monitoring
python start_monitoring.py --continuous
```

---

**🎯 Pro Tips:**
- Gunakan `python start_monitoring.py --continuous` untuk monitoring 24/7
- `python main_scanner.py` untuk security audit lengkap  
- Cek Telegram untuk notifikasi real-time
- Jalankan individual checkers untuk fokus pada area tertentu

**🔗 Need Help?**
- Cek `README.md` untuk panduan lengkap
- Cek `MONITORING_GUIDE.md` untuk advanced monitoring
- Cek `Dokumentasi Projek.md` untuk technical details
