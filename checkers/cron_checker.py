"""Modul untuk memeriksa konfigurasi cron job sistem.

Membaca file crontab sistem utama dan file-file di direktori cron.d/,
cron.hourly/, cron.daily/, cron.weekly/, dan cron.monthly/.
Memerlukan hak akses root untuk membaca beberapa direktori/file ini.
"""
import os
import platform
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output, capture_read_file_content
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Membaca beberapa file/direktori cron memerlukan hak akses root."

CRONTAB_FILE = "/etc/crontab"
CRON_DIRS = [
    "/etc/cron.d",
    "/etc/cron.hourly",
    "/etc/cron.daily",
    "/etc/cron.weekly",
    "/etc/cron.monthly"
]

def list_files_in_dir(dir_path, test_description):
    """Helper untuk mendaftar file dalam direktori dan menangkap outputnya."""
    captured_lines = [f"Mencoba mendaftar file di direktori: {dir_path} untuk tes '{test_description}'"]
    print_info(captured_lines[0])
    
    if not os.path.exists(dir_path):
        msg = f"Direktori {dir_path} tidak ditemukan."
        print_warning(msg)
        captured_lines.append(msg)
        return "\n".join(captured_lines)
    
    if not os.access(dir_path, os.R_OK | os.X_OK) and os.geteuid() != 0:
        msg = f"Tidak ada izin baca/eksekusi untuk direktori {dir_path} sebagai pengguna biasa."
        print_warning(msg)
        captured_lines.append(msg)
    try:
        files = os.listdir(dir_path)
        if files:
            msg_success = f"File ditemukan di {dir_path}:"
            print_success(msg_success)
            captured_lines.append(msg_success)
            for f_name in files:
                full_path = os.path.join(dir_path, f_name)
                is_dir_msg = " (Direktori)" if os.path.isdir(full_path) else " (File)"
                entry_msg = f"    - {f_name}{is_dir_msg}"
                print_info(entry_msg)
                captured_lines.append(entry_msg)
        else:
            msg_info = f"Tidak ada file di direktori {dir_path}."
            print_info(msg_info)
            captured_lines.append(msg_info)
    except PermissionError:
        msg_danger = f"Izin ditolak saat mengakses direktori {dir_path}."
        print_danger(msg_danger)
        captured_lines.append(msg_danger)
    except Exception as e:
        msg_danger = f"Gagal mendaftar file di {dir_path}: {e}"
        print_danger(msg_danger)
        captured_lines.append(msg_danger)
        
    return "\n".join(list(dict.fromkeys(captured_lines)))

def run_cron_checks():
    test_name = "Pemeriksaan Konfigurasi Cron Job Sistem"
    print_header(test_name)

    # Check for Windows - cron is not available on Windows
    if platform.system() == "Windows":
        print_warning("Cron tidak tersedia di Windows. Menggunakan Task Scheduler sebagai gantinya.")
        print_info("Untuk memeriksa task scheduler, gunakan: schtasks /query")
        return

    # Check if we have root privileges (Unix/Linux only)
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []

    output_crontab = capture_read_file_content(CRONTAB_FILE, f"File Crontab Utama ({CRONTAB_FILE})")
    if output_crontab and output_crontab.strip():
        all_raw_outputs.append(output_crontab)
        all_raw_outputs.append("\n---")

    for cron_dir in CRON_DIRS:
        dir_listing_output = list_files_in_dir(cron_dir, f"Direktori Cron {os.path.basename(cron_dir)}")
        if dir_listing_output and dir_listing_output.strip():
            all_raw_outputs.append(dir_listing_output)
        
        if cron_dir == "/etc/cron.d" and os.path.exists(cron_dir):
            try:
                for item_name in os.listdir(cron_dir):
                    item_path = os.path.join(cron_dir, item_name)
                    if os.path.isfile(item_path):
                        file_content_out = capture_read_file_content(item_path, f"File Cron: {item_name} di {cron_dir}")
                        if file_content_out and file_content_out.strip():
                            all_raw_outputs.append(file_content_out)
            except Exception as e:
                all_raw_outputs.append(f"Error saat memproses file di {cron_dir}: {e}")

        if dir_listing_output and dir_listing_output.strip():
             all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang signifikan dari pemeriksaan cron."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_cron_checks() 