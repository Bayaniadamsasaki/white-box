"""Modul untuk memeriksa informasi pengguna dan grup.

Ini membaca file /etc/passwd dan /etc/group untuk mendaftar pengguna dan grup,
serta melakukan pemeriksaan spesifik seperti mencari pengguna dengan UID 0 (selain root).
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_read_file_content
)

PASSWD_PATH = "/etc/passwd"
GROUP_PATH = "/etc/group"

def analyze_passwd_file_content(raw_content):
    """Menganalisis konten /etc/passwd yang sudah dibaca."""
    captured_lines = []
    users_with_uid_0 = []
    if not raw_content:
        return "Konten /etc/passwd kosong atau tidak dapat dibaca.", users_with_uid_0

    for line in raw_content.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split(":")
        if len(fields) >= 3:
            username = fields[0]
            uid = fields[2]
            if uid == "0" and username != "root":
                users_with_uid_0.append(username)
    
    if users_with_uid_0:
        msg = f"Peringatan: Ditemukan pengguna selain 'root' dengan UID 0: {', '.join(users_with_uid_0)}. Ini adalah risiko keamanan serius."
        print_danger(msg)
        captured_lines.append(msg)
    else:
        msg = "Tidak ada pengguna selain 'root' yang ditemukan dengan UID 0."
        print_success(msg)
        captured_lines.append(msg)
        
        
    return "\n".join(captured_lines), users_with_uid_0

def run_user_group_checks():
    test_name = "Pemeriksaan Pengguna dan Grup"
    print_header(test_name)
    all_raw_outputs = []

    desc_passwd = f"Membaca dan Menganalisis {PASSWD_PATH}"
    print_info(desc_passwd)
    passwd_content_full_output = capture_read_file_content(PASSWD_PATH, "Pengguna Sistem")
    all_raw_outputs.append(passwd_content_full_output)
    

    raw_passwd_text = ""
    if os.path.exists(PASSWD_PATH):
        try:
            with open(PASSWD_PATH, "r") as f_passwd:
                raw_passwd_text = f_passwd.read()
        except Exception as e:
            err_msg = f"Gagal membaca konten mentah {PASSWD_PATH} untuk analisis UID 0: {e}"
            print_danger(err_msg)
            all_raw_outputs.append(err_msg)

    if raw_passwd_text:
        analysis_output, _ = analyze_passwd_file_content(raw_passwd_text)
        if analysis_output:
             all_raw_outputs.append("\n--- Analisis Khusus UID 0 ---")
             all_raw_outputs.append(analysis_output)
    all_raw_outputs.append("\n---")

    desc_group = f"Membaca {GROUP_PATH}"
    print_info(desc_group)
    group_content_output = capture_read_file_content(GROUP_PATH, "Grup Sistem")
    all_raw_outputs.append(group_content_output)
    all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan pengguna dan grup."
        print_info(combined_raw_output)
    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_user_group_checks() 