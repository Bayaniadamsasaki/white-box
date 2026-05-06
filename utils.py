import os
import requests 
import json 
import subprocess 
import platform
import shutil
import sys
import atexit
from datetime import datetime
from dotenv import load_dotenv
import re
import time
import random
import threading

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
load_dotenv()

AUTO_LOG = os.getenv("AUTO_LOG", "true").strip().lower() != "false"
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE_PATH = None
_LOG_FILE_HANDLE = None
_LOG_LOCK = threading.Lock()
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")

def _sanitize_log_text(text):
    if text is None:
        return ""
    return _ANSI_ESCAPE_RE.sub("", str(text))

def _init_log_file():
    global LOG_FILE_PATH, _LOG_FILE_HANDLE
    if not AUTO_LOG:
        return
    try:
        log_dir = LOG_DIR
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        LOG_FILE_PATH = os.path.join(log_dir, f"scan_{timestamp}.log")
        _LOG_FILE_HANDLE = open(LOG_FILE_PATH, "a", encoding="utf-8")
        _LOG_FILE_HANDLE.write(f"{datetime.now().isoformat()} Auto-log enabled.\n")
        _LOG_FILE_HANDLE.flush()
    except Exception:
        LOG_FILE_PATH = None
        _LOG_FILE_HANDLE = None

def _close_log_file():
    global _LOG_FILE_HANDLE
    if _LOG_FILE_HANDLE:
        try:
            _LOG_FILE_HANDLE.flush()
            _LOG_FILE_HANDLE.close()
        except Exception:
            pass
        _LOG_FILE_HANDLE = None

def _log_line(message):
    if not _LOG_FILE_HANDLE:
        return
    cleaned = _sanitize_log_text(message).rstrip()
    if not cleaned:
        return
    with _LOG_LOCK:
        _LOG_FILE_HANDLE.write(f"{datetime.now().isoformat()} {cleaned}\n")
        _LOG_FILE_HANDLE.flush()

def _log_lines(lines):
    for line in lines:
        _log_line(line)

_init_log_file()
atexit.register(_close_log_file)

SUDO_READY = False
SUDO_UNAVAILABLE = False

def _has_sudo_command():
    return shutil.which("sudo") is not None

def has_sudo_access():
    if platform.system() == "Windows":
        return False
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return True
    if not _has_sudo_command():
        return False
    try:
        result = subprocess.run(["sudo", "-n", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False

def ensure_sudo_access():
    global SUDO_READY, SUDO_UNAVAILABLE
    if SUDO_READY:
        return True
    if SUDO_UNAVAILABLE:
        return False
    if platform.system() == "Windows":
        SUDO_UNAVAILABLE = True
        return False
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        SUDO_READY = True
        return True
    if not _has_sudo_command():
        SUDO_UNAVAILABLE = True
        return False
    if has_sudo_access():
        SUDO_READY = True
        return True
    if not sys.stdin.isatty():
        SUDO_UNAVAILABLE = True
        return False
    print_info("🔐 Memerlukan akses sudo untuk beberapa pemeriksaan. Masukkan password jika diminta...")
    try:
        result = subprocess.run(["sudo", "-v"])
    except Exception as e:
        print_warning(f"Gagal melakukan autentikasi sudo: {e}")
        SUDO_UNAVAILABLE = True
        return False
    if result.returncode == 0:
        SUDO_READY = True
        return True
    SUDO_UNAVAILABLE = True
    return False

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
    line = f"[+] {message}"
    _log_line(line)
    print(f"{Colors.OKGREEN}{line}{Colors.ENDC}")

def print_warning(message):
    line = f"[!] {message}"
    _log_line(line)
    print(f"{Colors.WARNING}{line}{Colors.ENDC}")

def print_danger(message):
    line = f"[-] {message}"
    _log_line(line)
    print(f"{Colors.FAIL}{line}{Colors.ENDC}")

def print_info(message):
    line = f"[*] {message}"
    _log_line(line)
    print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")

def print_header(message, char="-", color_code=Colors.HEADER):
    header_line = f"{char*3} {message} {char*3}"
    _log_line(header_line)
    print(f"{color_code}{Colors.BOLD}\n{header_line}{Colors.ENDC}")

def capture_command_output(command_input, test_description, suppress_output=False, shell=False):
    captured_output_lines = []
    command_to_run = command_input
    command_to_log = ""
    use_shell = shell

    if isinstance(command_input, list):
        command_to_log = " ".join(command_input)
        if any(token in ("|", ">", ">>", "<", "2>", "2>&1") for token in command_input):
            use_shell = True
            command_to_run = " ".join(command_input)
    else:
        command_to_log = str(command_input)

    uses_sudo = False
    if isinstance(command_input, list):
        uses_sudo = bool(command_input) and command_input[0] == "sudo"
    elif isinstance(command_input, str):
        uses_sudo = command_input.lstrip().startswith("sudo ")

    if not suppress_output:
        print_info(f"Menjalankan tes: {test_description} (Perintah: '{command_to_log}')")
    
    captured_output_lines.append(f"Test: {test_description} (Cmd: '{command_to_log}')")

    if uses_sudo and not ensure_sudo_access():
        msg = f"Peringatan: Akses sudo belum tersedia. Tes '{test_description}' dilewati."
        if not suppress_output:
            print_warning(msg)
        captured_output_lines.append(msg)
        _log_lines(captured_output_lines)
        return "\n".join(captured_output_lines)

    try:
        if use_shell and isinstance(command_to_run, list):
            command_to_run = " ".join(command_to_run)
        
        result = subprocess.run(command_to_run, capture_output=True, text=True, check=False, timeout=20, shell=use_shell)
        
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
    
    _log_lines(captured_output_lines)
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
    
    _log_lines(captured_output_lines)
    return "\n".join(captured_output_lines)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def _severity_rank(level):
    level_upper = str(level).strip().upper()
    try:
        return SEVERITY_ORDER.index(level_upper)
    except ValueError:
        return 1  # default MEDIUM

def _max_risk_level(a, b):
    return SEVERITY_ORDER[max(_severity_rank(a), _severity_rank(b))]

def _normalize_status_level(status_text, fallback="MEDIUM"):
    text = str(status_text).strip().upper()
    mapping = {
        "LOW": "LOW", "RENDAH": "LOW", "AMAN": "LOW", "INFO": "LOW",
        "MEDIUM": "MEDIUM", "SEDANG": "MEDIUM", "PERHATIAN": "MEDIUM", "WARNING": "MEDIUM", "WARN": "MEDIUM",
        "HIGH": "HIGH", "TINGGI": "HIGH", "BAHAYA": "HIGH", "DANGER": "HIGH",
        "CRITICAL": "CRITICAL", "KRITIS": "CRITICAL", "DARURAT": "CRITICAL", "SEVERE": "CRITICAL"
    }
    for key, value in mapping.items():
        if key in text:
            return value
    return _normalize_status_level(fallback, "MEDIUM") if fallback != "MEDIUM" else "MEDIUM"

def _infer_risk_level(raw_output):
    text = (raw_output or "").lower()

    critical_patterns = [
        "password kosong", "uid 0", "critical vulnerability", "remote code execution",
        "privilege escalation", "unauthorized root", "world-writable"
    ]
    high_patterns = [
        "brute force", "failed login", "permitrootlogin yes", "passwordauthentication yes",
        "auditd tidak aktif", "selinux disabled", "apparmor disabled", "risiko keamanan serius"
    ]
    medium_patterns = [
        "open port", "listening", "banner ssh", "ftp anonim", "warning", "outdated",
        "error", "failed", "refused", "timeout", "not found", "tidak aktif"
    ]

    if any(p in text for p in critical_patterns):
        return "CRITICAL"
    if any(p in text for p in high_patterns):
        return "HIGH"
    if any(p in text for p in medium_patterns):
        return "MEDIUM"
    return "LOW"

def _normalize_ai_status_in_text(suggestion_text, raw_output):
    lines = (suggestion_text or "").splitlines()
    fallback_level = _infer_risk_level(raw_output)
    status_found = False

    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("status:"):
            status_value = line.split(":", 1)[1].strip() if ":" in line else ""
            lines[idx] = f"Status: {_normalize_status_level(status_value, fallback_level)}"
            status_found = True
            break

    if not status_found:
        lines.insert(0, f"Status: {fallback_level}")

    return "\n".join(lines).strip()

def _extract_signal_lines(text, limit=3, clip_len=240):
    lines = [re.sub(r"\s+", " ", l.strip()) for l in str(text or "").splitlines() if l.strip()]
    if not lines:
        return []

    critical_kw = ["kritis", "critical", "password kosong", "uid 0", "world-writable", "unauthorized", "privilege escalation"]
    high_kw = ["bahaya", "danger", "risiko keamanan serius", "permitrootlogin yes", "passwordauthentication yes", "brute force"]
    medium_kw = ["peringatan", "warning", "error", "failed", "timeout", "refused", "not found", "tidak aktif", "open port", "listening"]

    scored = []
    for idx, line in enumerate(lines):
        low = line.lower()
        score = 0
        if any(k in low for k in critical_kw):
            score = 4
        elif any(k in low for k in high_kw):
            score = 3
        elif any(k in low for k in medium_kw) or line.startswith("[!]") or line.startswith("[-]"):
            score = 2

        if score > 0:
            clipped = line[:clip_len - 3] + "..." if len(line) > clip_len else line
            scored.append((score, idx, clipped))

    scored.sort(key=lambda x: (-x[0], x[1]))

    picked = []
    seen = set()
    for _, _, line in scored:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        picked.append(line)
        if len(picked) >= limit:
            break

    return picked

def _summarize_result_for_telegram(result, max_lines=8, line_clip=280):
    plain_lines = [re.sub(r"\s+", " ", l.strip()) for l in str(result or "").splitlines() if l.strip()]
    if not plain_lines:
        return "- Tidak ada output signifikan"

    signals = _extract_signal_lines(result, limit=max_lines, clip_len=line_clip)

    selected = []
    seen = set()

    for line in signals:
        key = line.lower()
        if key not in seen:
            selected.append(line)
            seen.add(key)

    for line in plain_lines:
        if len(selected) >= max_lines:
            break
        clipped = line[:line_clip - 3] + "..." if len(line) > line_clip else line
        key = clipped.lower()
        if key in seen:
            continue
        selected.append(clipped)
        seen.add(key)

    if not selected:
        first = plain_lines[0]
        first = first[:line_clip - 3] + "..." if len(first) > line_clip else first
        selected = [first]

    return "\n".join(f"- {line}" for line in selected[:max_lines])

def _clip_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3].rstrip() + "..."

def _extract_named_field(lines, field_name):
    prefix = field_name.lower() + ":"
    for line in lines:
        low = line.lower()
        if low.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""

def _extract_multiline_field(lines, field_name):
    target = field_name.lower() + ":"
    stop_prefixes = ("status:", "masalah:", "saran:", "catatan:", "tambahan:")
    collecting = False
    parts = []

    for line in lines:
        low = line.lower()
        if low.startswith(target):
            value = line.split(":", 1)[1].strip()
            if value:
                parts.append(value)
            collecting = True
            continue

        if collecting:
            if low.startswith(stop_prefixes):
                break
            parts.append(line)

    return " ".join(parts).strip()

def _build_recommendation_steps(raw_output, max_steps=3):
    low = str(raw_output or "").lower()
    steps = []

    if "permitrootlogin yes" in low or "passwordauthentication yes" in low:
        steps.append("Nonaktifkan PermitRootLogin dan PasswordAuthentication, lalu pakai SSH key-based authentication.")
    if "failed login" in low or "brute force" in low:
        steps.append("Aktifkan fail2ban dan batasi percobaan login berulang pada layanan akses remote.")
    if "world-writable" in low or "uid 0" in low or "password kosong" in low:
        steps.append("Audit akun/permission sensitif, hapus akses berlebih, dan perbaiki ownership serta mode file.")
    if "open" in low or "listening" in low or "port" in low:
        steps.append("Tutup port yang tidak diperlukan, dan batasi layanan internal agar tidak terekspos publik.")
    if "auditd tidak aktif" in low or "selinux disabled" in low or "apparmor disabled" in low:
        steps.append("Aktifkan auditd/SELinux/AppArmor sesuai distro untuk meningkatkan visibility dan proteksi host.")
    if "not found" in low or "timeout" in low or "refused" in low or "failed" in low:
        steps.append("Verifikasi paket terpasang, status service, dan dependensi command sebelum rerun scanning.")

    unique_steps = []
    seen = set()
    for step in steps:
        key = step.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_steps.append(step)
        if len(unique_steps) >= max_steps:
            break

    return unique_steps

def _compact_suggestion_for_telegram(suggestion, raw_output):
    normalized = _normalize_ai_status_in_text(suggestion, raw_output)
    lines = [l.strip() for l in normalized.splitlines() if l.strip()]

    status = _extract_named_field(lines, "Status")
    masalah = _extract_multiline_field(lines, "Masalah")
    saran = _extract_multiline_field(lines, "Saran")
    catatan = _extract_multiline_field(lines, "Catatan") or _extract_multiline_field(lines, "Tambahan")

    status = _normalize_status_level(status, _infer_risk_level(raw_output))
    if not masalah:
        signal = _extract_signal_lines(raw_output, limit=1)
        masalah = signal[0] if signal else "Perlu review manual singkat"
    if not saran:
        saran = "Lakukan validasi konfigurasi menyeluruh lalu prioritaskan perbaikan pada temuan berisiko tertinggi."

    masalah = _clip_text(re.sub(r"\s+", " ", masalah), 520)
    saran = _clip_text(re.sub(r"\s+", " ", saran), 900)
    catatan = _clip_text(re.sub(r"\s+", " ", catatan), 500) if catatan else ""

    show_priority_steps = os.getenv("SHOW_PRIORITY_STEPS", "true").strip().lower() == "true"
    langkah = _build_recommendation_steps(raw_output, max_steps=3)
    show_steps = show_priority_steps and langkah and _severity_rank(status) >= _severity_rank("MEDIUM")

    formatted = f"Status: {status}\nMasalah: {masalah}\nSaran: {saran}"
    if show_steps:
        langkah_text = "\n".join(f"{idx}. {step}" for idx, step in enumerate(langkah, 1))
        formatted += f"\nLangkah Prioritas:\n{langkah_text}"
    if catatan:
        formatted += f"\nCatatan: {catatan}"
    return formatted

def _split_text_chunks(text, max_len=2500):
    content = str(text or "").strip()
    if not content:
        return ["(kosong)"]

    chunks = []
    remaining = content
    while len(remaining) > max_len:
        split_idx = remaining.rfind("\n", 0, max_len)
        if split_idx < int(max_len * 0.5):
            split_idx = max_len
        chunks.append(remaining[:split_idx].strip())
        remaining = remaining[split_idx:].lstrip("\n")
    if remaining:
        chunks.append(remaining)
    return chunks

def _post_telegram_markdown(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
    response = requests.post(url, data=payload, timeout=20)
    response.raise_for_status()

def send_to_telegram(test_name, result, suggestion):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print_warning("Variabel lingkungan TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID tidak disetel. Lewati pengiriman ke Telegram.")
        return
    
    try:
        concise_result = _summarize_result_for_telegram(result, max_lines=8, line_clip=280)
        concise_suggestion = _compact_suggestion_for_telegram(suggestion, result)

        concise_result = _clip_text(concise_result, 2200)
        concise_suggestion = _clip_text(concise_suggestion, 1800)

        message = f"""*Pemeriksaan:* {escape_markdown_v2(test_name)}

*Hasil Test:*
{escape_markdown_v2(concise_result)}

*Analisis AI:*
{escape_markdown_v2(concise_suggestion)}
"""

        # Telegram hard limit ~4096 chars. Trim hasil test dulu jika masih terlalu panjang.
        escaped_message = message
        if len(escaped_message) > 3900:
            allowed_result = max(700, 2200 - (len(escaped_message) - 3900))
            concise_result = _clip_text(concise_result, allowed_result)
            message = f"""*Pemeriksaan:* {escape_markdown_v2(test_name)}

        *Hasil Test:*
        {escape_markdown_v2(concise_result)}

        *Analisis AI:*
        {escape_markdown_v2(concise_suggestion)}
        """

        _post_telegram_markdown(message)

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
    status_level = _infer_risk_level(raw_output)
    
    # Basic security assessment
    signal = _extract_signal_lines(raw_output, limit=1)
    specific_issue = signal[0] if signal else "Perlu review output"

    if any(keyword in output_lower for keyword in ['error', 'failed', 'denied', 'refused', 'timeout', 'not found']):
        status_level = _max_risk_level(status_level, "MEDIUM")
        return f"Status: {status_level}\nMasalah: {specific_issue}\nSaran: Review output dan perbaiki error yang terdeteksi"
    elif any(keyword in output_lower for keyword in ['password kosong', 'uid 0', 'world-writable', 'permitrootlogin yes']):
        status_level = _max_risk_level(status_level, "HIGH")
        return f"Status: {status_level}\nMasalah: {specific_issue}\nSaran: Prioritaskan perbaikan konfigurasi keamanan berisiko tinggi"
    elif any(keyword in output_lower for keyword in ['open', 'listening', 'accept']):
        status_level = _max_risk_level(status_level, "MEDIUM")
        return f"Status: {status_level}\nMasalah: {specific_issue}\nSaran: Pastikan hanya layanan/port yang diperlukan tetap terbuka"
    else:
        status_level = _normalize_status_level(status_level, "LOW")
        return f"Status: {status_level}\nMasalah: Tidak ada indikasi masalah langsung\nSaran: Lanjutkan monitoring rutin"

def create_enhanced_fallback(test_name, raw_output, partial_ai_response):
    """Create enhanced fallback when AI gives incomplete response"""
    output_lower = raw_output.lower()
    signal = _extract_signal_lines(raw_output, limit=1)
    specific_issue = signal[0] if signal else "Perlu review output"
    
    # Extract any useful info from partial AI response
    status = _normalize_status_level(partial_ai_response, _infer_risk_level(raw_output))
    
    # Rule-based assessment
    if any(keyword in output_lower for keyword in ['inactive', 'not found', 'failed', 'error', 'timeout', 'refused']):
        status = _max_risk_level(status, "MEDIUM")
        masalah = specific_issue
        saran = "Periksa instalasi dan konfigurasi layanan keamanan"
    elif any(keyword in output_lower for keyword in ['password kosong', 'uid 0', 'world-writable', 'permitrootlogin yes']):
        status = _max_risk_level(status, "HIGH")
        masalah = specific_issue
        saran = "Prioritaskan perbaikan konfigurasi keamanan berisiko tinggi"
    elif any(keyword in output_lower for keyword in ['fail2ban', 'ssh', 'hardening', 'open', 'listening']):
        status = _max_risk_level(status, "MEDIUM")
        masalah = specific_issue
        saran = "Pastikan hardening tools terpasang dan dikonfigurasi dengan benar"
    else:
        masalah = specific_issue
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
Status: LOW/MEDIUM/HIGH/CRITICAL
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
                            return _normalize_ai_status_in_text(suggestion, raw_output)
                
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