import os
import requests 
import json 
import subprocess 
from dotenv import load_dotenv
import re
import time
import random

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
load_dotenv()

class Colors:
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_success(message):
    print(f"{Colors.OKGREEN}[+] {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")

def print_danger(message):
    print(f"{Colors.FAIL}[-] {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}[*] {message}{Colors.ENDC}")

def print_header(message, char="-", color_code=Colors.HEADER):
    print(f"{color_code}{Colors.BOLD}\n{char*3} {message} {char*3}{Colors.ENDC}")

def capture_command_output(command_input, test_description, suppress_output=False, shell=False):
    captured_output_lines = []
    command_to_log = ""
    if isinstance(command_input, list):
        command_to_log = ' '.join(command_input)
        command_to_log = command_input

    if not suppress_output:
        print_info(f"Menjalankan tes: {test_description} (Perintah: '{command_to_log}')")
    
    captured_output_lines.append(f"Test: {test_description} (Cmd: '{command_to_log}')")

    try:
        if shell and isinstance(command_input, list):
            command_input = ' '.join(command_input)
        
        result = subprocess.run(command_input, capture_output=True, text=True, check=False, timeout=20, shell=shell)
        
        if result.returncode == 0:
            if not suppress_output:
                print_success(f"Tes '{test_description}' berhasil.")
                
            if result.stdout and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    captured_output_lines.append(f"    {line}")
            elif not result.stdout or not result.stdout.strip():
                 captured_output_lines.append("    (Tidak ada output standar)")
        else:
            if not suppress_output:
                print_danger(f"Tes '{test_description}' gagal dengan kode: {result.returncode}")
            
            if result.stdout and result.stdout.strip():
                if not suppress_output:
                    print_warning("    Output standar (saat gagal):")
                for line in result.stdout.strip().splitlines(): 
                    if not suppress_output: print(f"        {line}")
                    captured_output_lines.append(f"        [STDOUT] {line}")
            
            if result.stderr and result.stderr.strip():
                if not suppress_output:
                    print_warning("    Output error:")
                for line in result.stderr.strip().splitlines(): 
                    if not suppress_output: print(f"        {line}")
                    captured_output_lines.append(f"        [STDERR] {line}")
                
    except subprocess.TimeoutExpired:
        err_msg = f"Timeout saat menjalankan perintah untuk tes '{test_description}'."
        if not suppress_output: print_danger(err_msg)
        captured_output_lines.append(err_msg)
    except FileNotFoundError:
        cmd_name = command_input if shell else command_input[0]
        err_msg = f"Perintah '{cmd_name}' tidak ditemukan untuk tes '{test_description}'."
        if not suppress_output: print_danger(err_msg)
        captured_output_lines.append(err_msg)
    except Exception as e:
        err_msg = f"Kesalahan tidak terduga saat menjalankan perintah untuk tes '{test_description}': {e}"
        if not suppress_output: print_danger(err_msg)
        captured_output_lines.append(err_msg)
    
    final_output_str = "\n".join(captured_output_lines)
    return final_output_str

def capture_read_file_content(file_path, test_description, suppress_output=False):
    captured_output_lines = []
    
    def log_and_print(message, msg_type="info", to_capture=True, is_content=False):
        if to_capture:
            if is_content and message.strip():
                 for line_content in message.strip().splitlines():
                    captured_output_lines.append(f"    {line_content}")
            elif not is_content:
                 captured_output_lines.append(str(message))
        
        if not suppress_output:
            if msg_type == "info": print_info(message)
            elif msg_type == "success": print_success(message)
            elif msg_type == "warning": print_warning(message)
            elif msg_type == "danger": print_danger(message)
            elif not is_content : print(str(message))


    log_and_print(f"Test: {test_description} (File: {file_path})", "info", to_capture=True)
    
    if not suppress_output: print_info(f"Membaca file untuk tes: {test_description} (File: {file_path})")

    if not os.path.isabs(file_path):
        
        if not suppress_output: print_warning(f"Peringatan: Path file '{file_path}' tidak absolut.")

    if os.path.exists(file_path):
        try:
            if not os.access(file_path, os.R_OK):
                 try:
                     # Check if running as admin on Windows or root on Linux
                     import getpass
                     if getpass.getuser() != 'root':  # Simple check for non-root user
                         if not suppress_output: print_warning(f"Tidak ada izin baca untuk {file_path}. Hasil mungkin tidak lengkap.")
                 except:
                     pass  # Skip permission check on Windows
            
            with open(file_path, "r", errors='ignore') as f:
                content = f.read() 
                if content.strip():
                    
                    if not suppress_output: print_success(f"Berhasil membaca file '{file_path}' untuk tes '{test_description}'.")
                    
                    log_and_print(content, msg_type="content_internal", to_capture=True, is_content=True)
                else:
                    log_and_print(f"File '{file_path}' untuk tes '{test_description}' kosong.", "info", to_capture=True)
        except Exception as e:
            err_msg = f"Gagal membaca file '{file_path}' untuk tes '{test_description}': {e}"
            log_and_print(err_msg, "danger", to_capture=True)
    else:
        err_msg = f"File '{file_path}' tidak ditemukan untuk tes '{test_description}'."
        log_and_print(err_msg, "warning", to_capture=True)
    
    return "\n".join(captured_output_lines)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(test_name, result, suggestion):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print_warning("Variabel lingkungan TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID tidak disetel. Lewati pengiriman ke Telegram.")
        return

    max_len_part = 1900 
    truncated_result = result
    if len(result) > max_len_part:
        truncated_result = result[:max_len_part] + "\n\\.\\.\\. \\(hasil dipotong\\)"
    
    truncated_suggestion = suggestion
    if len(suggestion) > max_len_part:
        truncated_suggestion = suggestion[:max_len_part] + "\n\\.\\.\\. \\(saran dipotong\\)"

    message = f"""*Pemeriksaan:* {escape_markdown_v2(test_name)}

*Hasil Test:*
{escape_markdown_v2(truncated_result)}

*Saran:*
{escape_markdown_v2(truncated_suggestion)}
"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
    
    try:
        response = requests.post(url, data=payload, timeout=20)
        response.raise_for_status()
        print_info(f"Hasil dan saran test '{test_name}' dikirim ke Telegram.")
    except KeyboardInterrupt:
        print_warning(f"🛑 Pengiriman Telegram dibatalkan untuk '{test_name}'")
        return
    except requests.exceptions.Timeout:
        print_warning(f"⏰ Timeout saat mengirim '{test_name}' ke Telegram")
        return
    except requests.exceptions.ConnectionError:
        print_warning(f"🔌 Koneksi Telegram gagal untuk '{test_name}'")
        return
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print_danger(f"Gagal mengirim pesan '{test_name}' ke Telegram. Status: {e.response.status_code}, Response: {e.response.text}")
        else:
            print_danger(f"Gagal mengirim pesan '{test_name}' ke Telegram: {e}")
    except Exception as e:
        print_danger(f"Terjadi kesalahan tidak terduga saat mengirim pesan ke Telegram untuk '{test_name}': {e}")


# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def create_fallback_analysis(test_name, raw_output, reason):
    """Create manual analysis when AI is not available"""
    # Simple rule-based analysis
    output_lower = raw_output.lower()
    
    # Basic security assessment
    if any(keyword in output_lower for keyword in ['error', 'failed', 'denied', 'refused']):
        return "Status: PERHATIAN\nMasalah: Ditemukan error dalam output\nSaran: Review manual diperlukan"
    elif any(keyword in output_lower for keyword in ['root', 'admin', 'sudo', 'privilege']):
        return "Status: PERHATIAN\nMasalah: Akses privileged terdeteksi\nSaran: Verifikasi keamanan akses"
    elif any(keyword in output_lower for keyword in ['open', 'listening', 'accept']):
        return "Status: PERHATIAN\nMasalah: Port/layanan terbuka terdeteksi\nSaran: Pastikan hanya layanan perlu yang aktif"
    else:
        return "Status: AMAN\nMasalah: Tidak ada indikasi masalah langsung\nSaran: Lanjutkan monitoring rutin"

def create_enhanced_fallback(test_name, raw_output, partial_ai_response):
    """Create enhanced fallback when AI gives incomplete response"""
    output_lower = raw_output.lower()
    
    # Extract any useful info from partial AI response
    status = "PERHATIAN"
    if partial_ai_response:
        if "aman" in partial_ai_response.lower():
            status = "AMAN"
        elif "bahaya" in partial_ai_response.lower():
            status = "BAHAYA"
    
    # Rule-based assessment
    if any(keyword in output_lower for keyword in ['inactive', 'not found', 'failed', 'error']):
        masalah = "Service tidak aktif atau command tidak ditemukan"
        saran = "Periksa instalasi dan konfigurasi layanan keamanan"
    elif any(keyword in output_lower for keyword in ['fail2ban', 'ssh', 'hardening']):
        masalah = "Konfigurasi keamanan perlu review"
        saran = "Pastikan hardening tools terpasang dan dikonfigurasi dengan benar"
    else:
        masalah = "Perlu analisis manual lebih lanjut"
        saran = "Review output untuk identifikasi masalah keamanan"
    
    return f"""Status: {status}
Masalah: {masalah}
Saran: {saran}"""

def _env_true(name):
    return os.getenv(name, "false").strip().lower() == "true"

def _is_high_system_load(fast_mode=False):
    """Return True when 1-minute load average is too high for AI inference."""
    if not hasattr(os, "getloadavg"):
        return False
    try:
        load1, _, _ = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        default_threshold = 1.5 if fast_mode else (2.5 if cpu_count <= 4 else 4.0)
        max_load = float(os.getenv("AI_MAX_LOAD", str(default_threshold)))
        return load1 >= max_load
    except Exception:
        return False

def get_ollama_suggestion(test_name, raw_output):
    """Get security analysis from local Ollama model with comprehensive anti-truncation measures"""
    if not raw_output or not raw_output.strip():
        return "Tidak ada output mentah yang dihasilkan oleh tes, jadi tidak ada saran yang diminta dari AI."

    # Check if AI is disabled for slow servers
    disable_ai = os.getenv("DISABLE_AI_ANALYSIS", "false").lower() == "true"
    if disable_ai:
        print_info("🔧 AI analysis disabled - using fallback analysis only")
        return create_fallback_analysis(test_name, raw_output, "AI disabled for server performance")

    ubuntu_mode = _env_true("UBUNTU_MODE")
    fast_mode = _env_true("FAST_MODE")

    if fast_mode:
        print_warning("⚡ FAST_MODE aktif: AI dilewati untuk menjaga stabilitas server.")
        return create_fallback_analysis(test_name, raw_output, "FAST_MODE enabled")

    if ubuntu_mode and _is_high_system_load(fast_mode=False):
        print_warning("⚠️ Beban sistem tinggi (UBUNTU_MODE), AI dilewati sementara.")
        return create_fallback_analysis(test_name, raw_output, "High system load in UBUNTU_MODE")

    if not OLLAMA_MODEL:
        print_warning("⚠️ OLLAMA_MODEL belum di-set di .env. Menggunakan fallback analysis.")
        return create_fallback_analysis(test_name, raw_output, "Missing OLLAMA_MODEL")

    # Simple but effective prompt 
    prompt = f"""Analisis keamanan: {test_name}

Data:
{raw_output[:300]}

Jawab dengan format:
Status: AMAN/BAHAYA/PERHATIAN
Masalah: [masalah keamanan]
Saran: [solusi perbaikan]"""

    try:
        # Enhanced Ollama diagnostics
        print_info(f"🔍 Checking Ollama connection...")
        
        # Check if Ollama is running
        try:
            health_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if health_response.status_code != 200:
                print_warning("Ollama tidak dapat diakses.")
                return create_fallback_analysis(test_name, raw_output, "Ollama offline")
        except requests.exceptions.ConnectionError:
            print_warning("Ollama server tidak running.")
            return create_fallback_analysis(test_name, raw_output, "Connection failed")
        except requests.exceptions.Timeout:
            print_warning("Ollama connection timeout.")
            return create_fallback_analysis(test_name, raw_output, "Connection timeout")
        
        print_info("✅ Ollama OK. Model diambil dari OLLAMA_MODEL (.env).")
        
        # Baca pengaturan AI dari .env
        base_num_predict = int(os.getenv("AI_NUM_PREDICT", "500"))
        ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.1"))
        base_timeout = int(os.getenv("AI_TIMEOUT", "240"))
        base_retries = int(os.getenv("AI_RETRY_ATTEMPTS", "5"))
        base_min_length = int(os.getenv("AI_MIN_RESPONSE_LENGTH", "200"))

        # Profile konservatif untuk Ubuntu/VPS
        if ubuntu_mode:
            ai_num_predict = min(base_num_predict, 250)
            ai_timeout = min(base_timeout, 90)
            max_retries = min(base_retries, 2)
            min_length = min(base_min_length, 120)
            num_ctx = 768
            print_info("🐧 UBUNTU_MODE aktif: memakai profile AI konservatif.")
        else:
            ai_num_predict = base_num_predict
            ai_timeout = base_timeout
            max_retries = base_retries
            min_length = base_min_length
            num_ctx = 1024
        
        print_info(f"⏳ Memproses... (AI_NUM_PREDICT={ai_num_predict}, timeout={ai_timeout}s, {max_retries} percobaan)")
        
        # Loop untuk retry dengan validasi respons
        suggestion = ""
        for attempt in range(max_retries):
            try:
                # Prepare request dengan parameter yang disesuaikan per attempt
                if ubuntu_mode:
                    current_num_predict = ai_num_predict + (attempt * 50)
                    current_timeout = ai_timeout + (attempt * 15)
                else:
                    current_num_predict = ai_num_predict + (attempt * 150)
                    current_timeout = ai_timeout + (attempt * 30)
                
                data = {
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": ai_temperature,
                        "num_predict": current_num_predict,
                        "num_ctx": num_ctx,
                        "top_k": 10,
                        "top_p": 0.9
                        # Hapus stop tokens yang terlalu agresif
                    }
                }
                
                print_info(f"Attempt {attempt + 1}/{max_retries}: num_predict={current_num_predict}, timeout={current_timeout}s")
                
                response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=data, timeout=current_timeout)
                response.raise_for_status()
                
                # Parse respons
                response_json = response.json()
                if 'response' not in response_json:
                    continue
                
                suggestion = response_json['response'].strip()
                
                # Validasi kelengkapan yang lebih ketat
                if suggestion and len(suggestion) > min_length:
                    # Cek format yang diharapkan
                    has_status = 'Status:' in suggestion or 'status:' in suggestion.lower()
                    has_masalah = 'Masalah:' in suggestion or 'masalah:' in suggestion.lower()
                    has_saran = 'Saran:' in suggestion or 'saran:' in suggestion.lower() or 'rekomendasi' in suggestion.lower()
                    
                    if has_status and has_masalah and has_saran:
                        # Cek tanda-tanda respons terpotong yang lebih lengkap
                        truncation_signs = ['...', '(hasil dipotong)', 'terpotong', 'incomplete', 'truncated', 'cut off']
                        is_truncated = any(sign in suggestion.lower() for sign in truncation_signs)
                        
                        # Cek apakah berakhir dengan tiba-tiba (tidak ada penutup yang baik)
                        last_lines = suggestion.strip().split('\n')[-3:]  # 3 baris terakhir
                        last_text = ' '.join(last_lines).strip()
                        
                        # Respons dianggap lengkap jika berakhir dengan tanda baca atau kata penutup
                        ends_properly = (
                            last_text.endswith(('.', '!', '?', ':', ';')) or
                            any(word in last_text.lower() for word in ['selesai', 'lengkap', 'akhir', 'terima kasih', 'demikian'])
                        )
                        
                        # Cek apakah ada indikasi respons terpotong di tengah kalimat
                        middle_cutoff = any(line.endswith(('dan', 'atau', 'dengan', 'untuk', 'dari', 'ke', 'yang')) 
                                          for line in suggestion.split('\n')[-5:])
                        
                        if not (is_truncated or middle_cutoff) and (ends_properly or len(suggestion) > 800):
                            print_success(f"✅ AI analysis berhasil lengkap (attempt {attempt + 1})")
                            print_info(f"📊 Response length: {len(suggestion)} characters")
                            return suggestion
                
                print_warning(f"⚠️ Respons tidak lengkap pada attempt {attempt + 1} (len={len(suggestion)})")
                
            except requests.exceptions.Timeout:
                print_warning(f"⏰ Timeout pada attempt {attempt + 1}")
                continue
            except Exception as e:
                print_warning(f"Error pada attempt {attempt + 1}: {e}")
                continue
        
        # Semua percobaan gagal
        print_warning("⚠️ Semua percobaan AI gagal, menggunakan enhanced fallback...")
        return create_enhanced_fallback(test_name, raw_output, suggestion)
        
    except KeyboardInterrupt:
        print_warning(f"🛑 AI analysis dibatalkan oleh user untuk '{test_name}'")
        return create_enhanced_fallback(test_name, raw_output, "")
    except Exception as e:
        print_warning(f"🔌 Error Ollama untuk '{test_name}': {e}")
        return create_fallback_analysis(test_name, raw_output, f"AI error: {e}")

def get_ai_suggestion(test_name, raw_output):
    """Wrapper function for backward compatibility"""
    return get_ollama_suggestion(test_name, raw_output)

def wait_for_return():
    """Wait for user to press Enter to continue"""
    input(f"\n{Colors.OKCYAN}Tekan Enter untuk kembali ke menu...{Colors.ENDC}")