"""Modul untuk memeriksa keberadaan dan status dasar alat integritas file.

Saat ini memeriksa keberadaan AIDE (Advanced Intrusion Detection Environment)
dan Tripwire. Ini adalah pemeriksaan dasar dan tidak menjalankan pemindaian integritas.
Memerlukan hak akses root untuk beberapa pemeriksaan konfigurasi atau status layanan.
"""
import os
import platform
from utils import (
    print_info, print_success, print_warning,
    send_to_telegram, get_ai_suggestion,
    capture_command_output, print_header,
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Pemeriksaan alat integritas mungkin memerlukan root untuk detail penuh."

AIDE_CONF_PATHS = ["/etc/aide/aide.conf", "/etc/aide.conf"]
AIDE_DB_PATHS = ["/var/lib/aide/aide.db.gz", "/var/lib/aide/aide.db"]
TRIPWIRE_POL_PATHS = ["/etc/tripwire/tw.pol", "/etc/tripwire/twpol.txt"]
TRIPWIRE_CONF_PATHS = ["/etc/tripwire/tw.cfg", "/etc/tripwire/twcfg.txt"]
TRIPWIRE_DB_DIR = "/var/lib/tripwire"

def check_tool_presence_and_config(tool_name, which_cmd, conf_paths, db_paths_or_dir):
    """Helper untuk memeriksa keberadaan alat, file konfigurasi, dan database-nya."""
    captured_lines = []
    tool_found_via_which = False

    which_output = capture_command_output(["which", which_cmd], f"Lokasi Perintah {tool_name}")
    captured_lines.append(which_output)
    if which_cmd in which_output and ("tidak ditemukan" not in which_output.lower() and "not found" not in which_output.lower()):
        tool_found_via_which = True
        s_msg = f"Alat {tool_name} ({which_cmd}) ditemukan di sistem (via 'which')."
        print_success(s_msg)
        captured_lines.append(s_msg)
    else:
        w_msg = f"Alat {tool_name} ({which_cmd}) tidak ditemukan di PATH standar (via 'which'). Mungkin tidak terinstal atau PATH tidak lengkap."
        print_warning(w_msg)
        captured_lines.append(w_msg)

    if conf_paths:
        conf_found = False
        for conf_path in conf_paths:
           
            if os.path.exists(conf_path) and os.path.isfile(conf_path):
                s_msg = f"File konfigurasi {tool_name} ditemukan: {conf_path}"
                print_success(s_msg)
                captured_lines.append(s_msg)
                conf_found = True
                break
        if not conf_found:
            w_msg = f"Tidak ada file konfigurasi umum untuk {tool_name} yang ditemukan di {conf_paths}."
            print_warning(w_msg)
            captured_lines.append(w_msg)

    if db_paths_or_dir:
        db_found = False
        if isinstance(db_paths_or_dir, list):
            for db_path in db_paths_or_dir:
                if os.path.exists(db_path) and (os.path.isfile(db_path) or os.path.isdir(db_path)):
                    s_msg = f"Database/Direktori DB {tool_name} ditemukan: {db_path}"
                    print_success(s_msg)
                    captured_lines.append(s_msg)
                    db_found = True
                    break
        elif isinstance(db_paths_or_dir, str): # Asumsikan ini adalah direktori
            if os.path.exists(db_paths_or_dir) and os.path.isdir(db_paths_or_dir):
                s_msg = f"Direktori database {tool_name} ditemukan: {db_paths_or_dir}"
                print_success(s_msg)
                captured_lines.append(s_msg)
                db_found = True
        
        if not db_found:
            w_msg = f"Tidak ada database atau direktori database umum untuk {tool_name} yang ditemukan di {db_paths_or_dir}."
            print_warning(w_msg)
            captured_lines.append(w_msg)
            
    # Rekomendasi umum
    if tool_found_via_which:
        captured_lines.append(f"Rekomendasi: Jika {tool_name} terinstal, pastikan databasenya diinisialisasi dan ada jadwal pengecekan rutin.")
    else:
        captured_lines.append(f"Rekomendasi: Pertimbangkan untuk menginstal dan mengkonfigurasi alat integritas file seperti {tool_name} atau yang serupa.")

    return "\n".join(list(dict.fromkeys(captured_lines)))

def run_integrity_checks():
    test_name = "Pemeriksaan Alat Integritas File (AIDE, Tripwire)"
    print_header(test_name)

    # Check for Windows - integrity tools are different on Windows
    if platform.system() == "Windows":
        print_warning("Alat integritas AIDE/Tripwire tidak tersedia di Windows.")
        print_info("Untuk Windows, gunakan tools seperti: FCIV, PowerShell Get-FileHash, atau Windows Defender.")
        return

    # Check if we have root privileges (Unix/Linux only)
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []

    print_info("--- Memeriksa AIDE ---")
    aide_output = check_tool_presence_and_config(
        tool_name="AIDE", 
        which_cmd="aide", 
        conf_paths=AIDE_CONF_PATHS, 
        db_paths_or_dir=AIDE_DB_PATHS
    )
    if aide_output and aide_output.strip():
        all_raw_outputs.append(aide_output)
    all_raw_outputs.append("\n---")

    print_info("--- Memeriksa Tripwire ---")
    tripwire_output = check_tool_presence_and_config(
        tool_name="Tripwire", 
        which_cmd="tripwire", 
        conf_paths=TRIPWIRE_CONF_PATHS + TRIPWIRE_POL_PATHS, # Gabungkan config dan policy paths
        db_paths_or_dir=TRIPWIRE_DB_DIR
    )
    if tripwire_output and tripwire_output.strip():
        all_raw_outputs.append(tripwire_output)
    all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan integritas."
        if os.geteuid() != 0:
            combined_raw_output += f" {REQUIRED_ROOT_MESSAGE}"
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    if os.path.basename(__file__) == "integrity_checker_stub.py":
        print_warning("Harap ganti nama file ini menjadi integrity_checker.py untuk menjalankan contoh.")
    else:
        run_integrity_checks() 