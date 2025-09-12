"""Modul ini bertanggung jawab untuk memeriksa file /etc/securetty.

File /etc/securetty menentukan dari TTY mana saja pengguna root diizinkan untuk login.
Modul ini akan membaca file tersebut, menampilkan isinya, dan memberikan catatan terkait
konfigurasi yang ditemukan.
"""
import os
import io
import contextlib
from utils import print_info, print_success, print_warning, print_danger, print_header, send_to_telegram, get_gemini_suggestion

def check_securetty_file_content():
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(msg)
        if msg_type == "info":
            print_info(msg)
        elif msg_type == "success":
            print_success(msg)
        elif msg_type == "warning":
            print_warning(msg)
        elif msg_type == "danger":
            print_danger(msg)
        else:
            print(msg) # Fallback

    custom_print("Mencoba memeriksa file /etc/securetty...", "info")
    securetty_file = "/etc/securetty"
    
    if not os.path.exists(securetty_file):
        custom_print(f"File {securetty_file} tidak ditemukan.", "danger")
        custom_print("Ini berarti root dapat login dari TTY mana pun yang tidak dibatasi oleh metode lain (misalnya PAM).", "warning")
        custom_print("Pada sistem modern, pembatasan login root seringkali lebih dikontrol melalui konfigurasi SSHD (PermitRootLogin no) dan PAM.", "info")
        return "\n".join(captured_output)

    try:
        with open(securetty_file, "r") as f:
            content = f.read().strip()
            if content:
                custom_print(f"Isi {securetty_file} (TTY tempat root diizinkan login langsung):", "success")
                lines = content.splitlines()
                suspicious_ttys = ["ttyS", "tts/", "vc/" , "pts/"] 
                has_suspicious = False
                valid_lines_found = False
                for tty_line in lines:
                    tty_line = tty_line.strip()
                    if not tty_line or tty_line.startswith("#"):
                        continue
                    valid_lines_found = True
                    custom_print(f"    - {tty_line}", "info")
                    if any(susp_tty in tty_line for susp_tty in suspicious_ttys) and not tty_line.startswith("ttyS"):
                         if not (tty_line.startswith("vc/") and tty_line[3:].isdigit()): 
                            custom_print(f"        Catatan: Entri '{tty_line}' mungkin perlu ditinjau lebih lanjut.", "warning")
                            has_suspicious = True
                
                if not valid_lines_found:
                     custom_print(f"File {securetty_file} ada tetapi kosong atau hanya berisi komentar. Ini berarti root tidak bisa login dari TTY mana pun (jika file ini dihormati oleh sistem login).", "warning")
                elif not has_suspicious:
                     custom_print("Tidak ada entri TTY yang jelas mencurigakan ditemukan.", "success")

            else:
                custom_print(f"File {securetty_file} kosong. Ini biasanya berarti root tidak diizinkan login dari TTY mana pun jika file ini digunakan oleh sistem login.", "warning")
        
        custom_print("\nTujuan /etc/securetty adalah untuk membatasi terminal (TTY) fisik atau virtual tempat pengguna root dapat login secara langsung.", "info")
        custom_print("Jika file ini tidak ada, root dapat login dari TTY mana pun (kecuali dibatasi oleh PAM atau konfigurasi layanan seperti SSH).", "info")
        custom_print("Jika file ada dan kosong, root tidak dapat login dari TTY mana pun.", "info")
        custom_print("Untuk login SSH sebagai root, pengaturan 'PermitRootLogin' di sshd_config lebih diutamakan.", "info")

    except Exception as e:
        custom_print(f"Gagal membaca atau memproses {securetty_file}: {e}", "danger")
    
    return "\n".join(captured_output)

def run_securetty_checks():
    test_name = "Pengecekan /etc/securetty"
    print_header(test_name)
    
    raw_output = check_securetty_file_content()
    
    if not raw_output.strip():
        raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan securetty."
        print_info(raw_output)

    gemini_saran = get_gemini_suggestion(test_name, raw_output)
    

    send_to_telegram(test_name, raw_output, gemini_saran)

if __name__ == '__main__':
    run_securetty_checks() 