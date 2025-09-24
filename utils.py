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
                 if os.geteuid() != 0:
                     
                     if not suppress_output: print_warning(f"Tidak ada izin baca untuk {file_path}. Hasil mungkin tidak lengkap.")
            
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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
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

def get_ollama_suggestion(test_name, raw_output):
    """Get security analysis from local Ollama model"""
    if not raw_output or not raw_output.strip():
        return "Tidak ada output mentah yang dihasilkan oleh tes, jadi tidak ada saran yang diminta dari AI."

    # Check if AI is disabled for slow servers
    disable_ai = os.getenv("DISABLE_AI_ANALYSIS", "false").lower() == "true"
    if disable_ai:
        print_info("🔧 AI analysis disabled - using fallback analysis only")
        return create_fallback_analysis(test_name, raw_output, "AI disabled for server performance")

    prompt = f"""Analisis singkat '{test_name}':

Data: {raw_output[:1000]}

Jawab SINGKAT (maks 3 baris):
Status: [AMAN/BAHAYA/PERHATIAN]
Masalah: [1 kalimat]
Saran: [1 kalimat]"""

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
        
        # Check if model is available
        try:
            models_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            models_data = models_response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            if OLLAMA_MODEL not in available_models:
                print_warning(f"Model {OLLAMA_MODEL} tidak ditemukan. Available: {available_models}")
                return create_fallback_analysis(test_name, raw_output, f"Model {OLLAMA_MODEL} not found")
                
        except Exception as e:
            print_warning(f"Cannot check available models: {e}")
        
        print_info(f"✅ Ollama OK. Model: {OLLAMA_MODEL}")
        
        # Prepare request for Ollama with fast parameters for llama3.2:1b
        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,      # Lower for faster, more focused responses
                "num_predict": 100,      # Much shorter output - max ~50-70 words
                "num_ctx": 512,          # Smaller context for speed
                "top_k": 10,             # Very limited choices for speed
                "top_p": 0.7
            }
        }
        
        print_info(f"Requesting analysis from Ollama model '{OLLAMA_MODEL}'...")
        
        # Get configurable timeout for slow servers
        ai_timeout = int(os.getenv("AI_TIMEOUT", "60"))  # Default 60s, configurable up to 180s
        print_info(f"⏳ Processing... (max {ai_timeout} seconds for server compatibility)")
        
        # Configurable timeout with retry for Ubuntu servers
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=data, timeout=ai_timeout)
                response.raise_for_status()
                break  # Success, exit retry loop
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print_warning(f"⏰ Timeout attempt {attempt + 1}, retrying with longer timeout...")
                    ai_timeout += 60  # Add 60s for next attempt
                    continue
                else:
                    raise  # Final attempt failed
        response.raise_for_status()
        
        response_json = response.json()
        if 'response' in response_json:
            suggestion = response_json['response'].strip()
            
            # Clean up DeepSeek-R1 thinking content but preserve analysis
            if any(phrase in suggestion.lower() for phrase in [
                'hmm', 'okay', 'wait', 'the user wants', 'thinking...'
            ]):
                import re
                
                # Remove thinking tags
                suggestion = re.sub(r'<think>.*?</think>', '', suggestion, flags=re.DOTALL)
                suggestion = re.sub(r'</?think>', '', suggestion)
                suggestion = re.sub(r'Thinking\.\.\..*?done thinking\.', '', suggestion, flags=re.DOTALL)
                
                # Split into lines and filter
                lines = suggestion.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                        
                    # Keep lines that look like actual analysis results
                    if any(keyword in line for keyword in [
                        'Status:', 'Masalah:', 'Saran:', 'AMAN', 'BAHAYA', 
                        'SSH', 'root login', 'password', 'authentication',
                        'konfigurasi', 'keamanan', 'server'
                    ]):
                        cleaned_lines.append(line)
                        continue
                    
                    # Skip obvious thinking lines
                    line_lower = line.lower()
                    if any(skip_phrase in line_lower for skip_phrase in [
                        'hmm', 'okay', 'wait', 'aku melihat', 'aku perlu',
                        'the user wants', 'user meminta', 'dalam konteks',
                        'hal-hal yang penting', 'penggunaan algoritma'
                    ]):
                        continue
                    
                    # Keep other substantial lines
                    if len(line_clean) > 20:
                        cleaned_lines.append(line)
                
                suggestion = '\n'.join(cleaned_lines).strip()
                
                # If result is too short, create simple fallback
                if len(suggestion) < 100:
                    suggestion = f"""Status: PERLU ANALISIS MANUAL
Masalah: AI analysis menghasilkan output yang perlu dibersihkan
Saran: Review manual hasil tes untuk mendapatkan insight keamanan yang tepat"""
            
            # Check if response seems truncated - simplified detection
            if suggestion:
                # Only check for obvious truncation indicators
                is_truncated = (
                    suggestion.endswith('...') or 
                    suggestion.endswith('ter') or  
                    suggestion.endswith('men') or
                    suggestion.endswith('kan') or
                    suggestion.endswith('dan') or
                    suggestion.endswith('yang') or
                    suggestion.endswith(',') or
                    # Check if too short (likely truncated)
                    len(suggestion) < 150
                )
                
                if is_truncated:
                    print_warning("⚠️ Response appears truncated, requesting completion...")
                    
                    # Simple continuation request
                    continue_prompt = f"""Lanjutkan analisis yang belum selesai ini:

{suggestion}

Lanjutkan dari bagian yang terpotong dan selesaikan analisis:"""
                    
                    continue_data = {
                        "model": OLLAMA_MODEL,
                        "prompt": continue_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "top_p": 0.9,
                            "num_predict": 500,      # Enough for completion
                            "num_ctx": 2048,
                            "top_k": 40
                        }
                    }
                    
                    try:
                        continue_response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                                                        json=continue_data, timeout=90)
                        if continue_response.status_code == 200:
                            continue_json = continue_response.json()
                            if 'response' in continue_json:
                                continuation = continue_json['response'].strip()
                                
                                # Clean continuation more thoroughly
                                if '<think>' in continuation:
                                    import re
                                    continuation = re.sub(r'<think>.*?</think>', '', continuation, flags=re.DOTALL)
                                    continuation = re.sub(r'</?think>', '', continuation)
                                    continuation = continuation.strip()
                                    
                                    # Remove thinking-style content
                                    lines = continuation.split('\n')
                                    cleaned_lines = []
                                    for line in lines:
                                        if any(phrase in line.lower() for phrase in [
                                            'baik, saya akan', 'mari kita', 'pertama-tama',
                                            'sekarang mari', 'analisis keamanan lanjutan',
                                            'mari kita lanjutkan'
                                        ]):
                                            continue
                                        if line.strip():
                                            cleaned_lines.append(line)
                                    continuation = '\n'.join(cleaned_lines).strip()
                                
                                if continuation and len(continuation) > 30:
                                    suggestion = suggestion + "\n\n" + continuation
                                    print_success("✅ Got continuation response")
                    except Exception as e:
                        print_warning(f"Could not get continuation: {e}")
                
                print_success("✅ AI analysis completed successfully")
                print_info(f"📊 Response length: {len(suggestion)} characters")
                return suggestion
            else:
                print_warning("⚠️ Ollama returned empty response after cleaning")
                return f"AI analysis tidak menghasilkan output untuk '{test_name}'. Review manual diperlukan."
        else:
            print_warning("⚠️ Unexpected Ollama response format")
            return f"AI analysis gagal (format response tidak valid) untuk '{test_name}'"
            
    except KeyboardInterrupt:
        print_warning(f"🛑 AI analysis dibatalkan oleh user untuk '{test_name}'")
        return f"""**STATUS:** PERLU REVIEW MANUAL

**TEMUAN:**
• Analisis AI dibatalkan atau timeout
• Hasil tes mentah tersedia untuk review manual

**REKOMENDASI:**
1. Review manual hasil tes: {test_name}
    except requests.exceptions.Timeout:
        print_warning(f"⏰ Ollama timeout untuk '{test_name}' - Using fallback analysis")
        return create_fallback_analysis(test_name, raw_output, "AI timeout after 30s")
    except requests.exceptions.ConnectionError:
        print_warning(f"🔌 Gagal terhubung ke Ollama untuk '{test_name}'")
        return create_fallback_analysis(test_name, raw_output, "Ollama offline")

**REKOMENDASI:**
1. Jalankan: ollama serve
2. Pastikan model tersedia: ollama list
3. Atau disable AI: set USE_OLLAMA=false di .env

**PRIORITAS:** Fix Ollama connection atau review manual"""
    except requests.exceptions.RequestException as e:
        print_warning(f"📡 Error komunikasi Ollama untuk '{test_name}': {e}")
        return f"""**STATUS:** ERROR - PERLU REVIEW

**TEMUAN:**
• Error komunikasi dengan Ollama: {str(e)[:100]}
• Mungkin ada masalah network atau konfigurasi

**REKOMENDASI:**
1. Check Ollama status: ollama list
2. Restart Ollama service
3. Review manual hasil tes sementara

**PRIORITAS:** Troubleshoot Ollama atau manual review"""
    except Exception as e:
        print_warning(f"❌ Error tidak terduga dengan Ollama untuk '{test_name}': {e}")
        return f"""**STATUS:** UNEXPECTED ERROR - PERLU REVIEW

**TEMUAN:**
• Error tidak terduga: {str(e)[:100]}
• Sistem AI mengalami masalah

**REKOMENDASI:**
1. Review manual hasil tes: {test_name}
2. Check log sistem untuk detail error
3. Restart aplikasi jika perlu

**PRIORITAS:** Manual review segera diperlukan"""

def get_ai_suggestion(test_name, raw_output):
    """Get security analysis from Ollama AI model"""
    return get_ollama_suggestion(test_name, raw_output)

if __name__ == '__main__':
    print_header("Contoh Penggunaan Utilitas Cetak")
    print_success("Ini adalah pesan sukses.")
    print_warning("Ini adalah pesan peringatan.")
    print_danger("Ini adalah pesan bahaya/error.")
    print_info("Ini adalah pesan informasi.")

    test_name_example = "Contoh Test Keamanan Internal"
    print_header("Contoh capture_command_output (normal)")
    cmd_output_normal = capture_command_output(["echo", "Ini output sukses"], "Tes Echo Sukses")
    print_info(f"Captured (untuk log/telegram):\n{cmd_output_normal}\n")

    print_header("Contoh capture_command_output (gagal)")
    cmd_output_gagal = capture_command_output(["ls", "/folderTidakAda"], "Tes ls Gagal")
    print_info(f"Captured (untuk log/telegram):\n{cmd_output_gagal}\n")

    print_header("Contoh capture_command_output (sukses tanpa output)")

    cmd_output_no_stdout = capture_command_output(["true"], "Tes Perintah True")
    print_info(f"Captured (untuk log/telegram):\n{cmd_output_no_stdout}\n")

    dummy_file_path = "dummy_test_file_utils.txt"
    print_header("Contoh capture_read_file_content (file ada)")
    with open(dummy_file_path, "w") as df:
        df.write("Baris pertama.\nBaris kedua.")
    file_content_normal = capture_read_file_content(dummy_file_path, "Tes Baca File Ada")
    print_info(f"Captured (untuk log/telegram):\n{file_content_normal}\n")
    os.remove(dummy_file_path)

    print_header("Contoh capture_read_file_content (file kosong)")
    with open(dummy_file_path, "w") as df:
        df.write("")
    file_content_empty = capture_read_file_content(dummy_file_path, "Tes Baca File Kosong")
    print_info(f"Captured (untuk log/telegram):\n{file_content_empty}\n")
    os.remove(dummy_file_path)
    
    print_header("Contoh capture_read_file_content (file tidak ada)")
    file_content_not_found = capture_read_file_content("file_tidak_ada_sama_sekali.txt", "Tes Baca File Tidak Ada")
    print_info(f"Captured (untuk log/telegram):\n{file_content_not_found}\n")
    ai_advice = get_ai_suggestion(test_name_example, cmd_output_normal)

    send_to_telegram(test_name_example, cmd_output_normal, ai_advice)