# NULL Security Monitor - Real-time Attack Detection

## Overview

Sistem monitoring real-time untuk mendeteksi serangan dari blackbox security tools secara otomatis. Sistem ini akan:

- **Monitor log files** secara real-time untuk mendeteksi aktivitas mencurigakan
- **Detect network activities** yang menunjukkan pola serangan
- **Analyze threats** menggunakan AI (Ollama llama3.2:1b) secara otomatis
- **Send alerts** melalui Telegram ketika serangan terdeteksi
- **Support continuous monitoring** tanpa perlu menjalankan scan berulang

## Supported Attack Tools Detection

Sistem dapat mendeteksi aktivitas dari tools berikut:

### Subdomain Enumeration
- **Subfinder** - Subdomain discovery tool
- **Amass** - Network mapping & attack surface discovery

### Web Crawling & Discovery  
- **Katana** - Next-generation crawling framework
- **GoSpider** - Fast web spider
- **Hakrawler** - Web crawler for gathering URLs

### Web Fuzzing & Testing
- **FFUF** - Fast web fuzzer  
- **Gobuster** - Directory/file & DNS busting tool
- **Dirb** - Web content scanner
- **Wfuzz** - Web application fuzzer

### Vulnerability Scanning
- **Nuclei** - Vulnerability scanner with templates
- **Nikto** - Web server vulnerability scanner
- **SQLMap** - SQL injection testing tool

### Network Scanning
- **Nmap** - Network discovery & security auditing
- **Masscan** - Fast port scanner
- **Zmap** - Fast network scanner

### Parameter Discovery
- **ParamSpider** - Parameter mining tool
- **Arjun** - HTTP parameter discovery
- **x8** - Hidden parameters discovery

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `env.example` to `.env` dan isi konfigurasi:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Ollama AI Configuration (Local)
OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Test Configuration
```bash
python utils.py  # Test Telegram & AI connectivity
```

## Usage Modes

### Mode 1: Continuous Monitoring (Recommended)

Monitoring terus-menerus di background yang akan langsung analisis ketika serangan terdeteksi.

```bash
# Interactive mode
python start_monitoring.py

# Direct continuous mode
python start_monitoring.py --continuous

# Atau melalui main scanner
python main_scanner.py
# Pilih 'y' ketika ditanya untuk continuous monitoring
```

**Cara Kerja:**
1. Sistem berjalan di background terus-menerus
2. Monitor log files secara real-time
3. Detect network activity patterns
4. Ketika serangan terdeteksi → **LANGSUNG** analisis AI + notifikasi Telegram
5. Terus monitoring tanpa henti

### Mode 2: One-time Scan

Scan sekali untuk melihat serangan yang sedang berlangsung saat ini.

```bash
# One-time scan mode
python start_monitoring.py --scan

# Atau langsung
python -m monitoring.security_monitor
```

## Real-time Detection Examples

### Ketika Subfinder Menyerang:
```
🚨 SERANGAN TERDETEKSI! [2025-08-13 23:45:12]
Tool: subfinder
Source: log
Details: GET /api/v1/users HTTP/1.1 User-Agent: subfinder/2.6.3

🔍 Melakukan analisis otomatis...
🤖 Mendapatkan analisis AI...
📱 Mengirim notifikasi darurat...
✅ Analisis dan notifikasi selesai!
🛡️ Continuing monitoring...
```

### Ketika Nmap Scanning:
```
🚨 SERANGAN TERDETEKSI! [2025-08-13 23:46:30]
Tool: nmap  
Source: network
Details: Multiple connections from 192.168.1.100 to port 80

🔍 Melakukan analisis otomatis...
🤖 Mendapatkan analisis AI...
📱 Mengirim notifikasi darurat...
✅ Analisis dan notifikasi selesai!
🛡️ Continuing monitoring...
```

## Integration dengan Main Scanner

Setelah menjalankan `python main_scanner.py`, sistem akan menanyakan:

```
--- Opsi Real-time Security Monitoring ---
[*] Scan awal telah selesai. Anda dapat memulai monitoring real-time untuk mendeteksi serangan.
[*] Mode monitoring akan:
[*] • Memantau log files secara real-time
[*] • Mendeteksi aktivitas tools seperti Subfinder, Katana, FFUF, Nuclei, Nmap, ParamSpider
[*] • Melakukan analisis AI otomatis ketika serangan terdeteksi
[*] • Mengirim notifikasi Telegram langsung

Apakah ingin memulai continuous monitoring? (y/n):
```

Pilih **'y'** untuk langsung mulai monitoring tanpa perlu menjalankan script terpisah.

## Testing dengan Blackbox Tools

### Testing Red Team vs Blue Team

1. **Jalankan continuous monitoring** terlebih dahulu:
   ```bash
   python start_monitoring.py --continuous
   ```

2. **Simulate attack** dengan blackbox tools:
   ```bash
   # Subfinder test
   subfinder -d example.com
   
   # FFUF test  
   ffuf -u http://target.com/FUZZ -w wordlist.txt
   
   # Nmap test
   nmap -sS target.com
   
   # Nuclei test
   nuclei -u http://target.com
   ```

3. **Monitor deteksi** di terminal monitoring - sistem akan langsung detect dan analisis otomatis.

### Log Monitoring Paths

Sistem akan otomatis monitor file log berikut:

**Linux:**
- `/var/log/apache2/access.log`
- `/var/log/nginx/access.log`
- `/var/log/auth.log`
- `/var/log/syslog`

**Windows:**
- `C:\Windows\System32\LogFiles\W3SVC1\`
- `C:\inetpub\logs\LogFiles\W3SVC1\`

**Local:**
- `./logs/`
- `./access.log`
- `./error.log`

## Advanced Features

### Custom Log Patterns
Sistem menggunakan pattern matching untuk detect tools:

```python
'subfinder': {
    'patterns': [
        r'subfinder',
        r'User-Agent:.*subfinder',
        r'subdomain.*enumeration'
    ]
}
```

### Network Pattern Detection  
Detect suspicious network activities:
- Multiple connections ke port yang sama dalam waktu singkat
- Scanning patterns dari IP yang sama
- Connections ke suspicious ports (22, 21, 80, 443, 3389, etc.)

### AI-Powered Analysis
Ketika serangan terdeteksi, sistem akan:
1. Analyze attack pattern
2. Get contextual information  
3. Generate security recommendations
4. Send comprehensive report via Telegram

## Troubleshooting

### Common Issues

1. **"psutil not available"**
   ```bash
   pip install psutil
   ```

2. **"No log files found"**
   - Pastikan aplikasi web berjalan dan menggenerate logs
   - Check permission untuk akses log files
   - Buat local log files untuk testing

3. **"Telegram/AI error"**
   - Check `.env` configuration
   - Test connectivity: `python utils.py`
   - Verify API keys

### Performance Tips

- Monitoring menggunakan threads untuk performance optimal
- Log files di-check setiap 2 detik
- Network monitoring setiap 3 detik  
- Main loop check setiap 5 detik

## Security Considerations

- **Root/Admin privileges** recommended untuk network monitoring
- **Log file permissions** harus readable oleh user
- **API keys** disimpan aman di `.env`
- **Network monitoring** bisa false positive pada aktivitas normal

## Benefits vs Traditional Scanning

### Traditional Approach (Manual):
```
1. Run main_scanner.py
2. Wait for completion  
3. Check results
4. Manually run again later
5. Miss real-time attacks
```

### Continuous Monitoring Approach:
```
1. Run main_scanner.py ONCE
2. Enable continuous monitoring
3. System runs in background  
4. Auto-detect attacks immediately
5. Auto-analysis + notifications
6. Never miss attacks
```

**Result: Anda tidak perlu "males jalanin terus menerus main scanner" - sistem otomatis handle everything!**

## File Structure

```
null/
├── start_monitoring.py      # Main entry point untuk monitoring
├── monitoring/
│   └── security_monitor.py  # Core monitoring engine  
├── main_scanner.py         # Integrated dengan monitoring option
├── utils.py               # Telegram & AI integration
├── .env                   # Configuration file
└── requirements.txt       # Dependencies
```

---

**Ready to use!** Jalankan `python start_monitoring.py --continuous` dan sistem akan handle semua deteksi + analisis otomatis ketika blackbox tools menyerang! 🛡️
