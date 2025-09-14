"""Modul ini bertanggung jawab untuk memeriksa file banner pra-login.

File seperti /etc/issue dan /etc/issue.net ditampilkan kepada pengguna
sebelum mereka login. Modul ini membaca file-file tersebut, menganalisis
kontennya untuk potensi kebocoran informasi atau ketiadaan peringatan hukum,
dan memberikan rekomendasi.
"""
import os
from utils import (print_info, print_success, print_warning, 
                   print_danger, print_header, send_to_telegram, 
                   get_ai_suggestion)

def capture_banner_file_check(file_path, banner_type):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(msg)
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(msg)

    custom_print(f"Memeriksa file banner {banner_type}: {file_path}...", "info")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
                if content:
                    custom_print(f"Isi {file_path}:", "success")
                    print(content) 
                    captured_output.append(content)
                    
                    sensitive_keywords = ["kernel", "ubuntu", "debian", "centos", "red hat", "\\l", "\\m", "\\r", "\\s", "\\v"]
                    content_lower = content.lower()
                    found_sensitive = [kw for kw in sensitive_keywords if kw in content_lower]
                    
                    if "warning" not in content_lower and "unauthorized" not in content_lower and "authorised" not in content_lower:
                        custom_print(f"Rekomendasi: Pertimbangkan untuk menambahkan banner peringatan hukum ke {file_path}.", "warning")
                    else:
                        custom_print(f"Banner peringatan standar tampaknya ada di {file_path}.", "success")
                    
                    actual_sensitive_info = [kw for kw in found_sensitive if kw not in ["warning", "unauthorized", "authorised"]]
                    if actual_sensitive_info:
                        custom_print(f"Peringatan: {file_path} mungkin menampilkan informasi sistem yang bisa sensitif (misalnya: {actual_sensitive_info}).", "warning")
                        custom_print("Rekomendasi: Hapus informasi detail sistem dari banner jika tidak diperlukan.", "warning")
                else:
                    custom_print(f"File {file_path} kosong.", "info")
        except Exception as e:
            custom_print(f"Gagal membaca {file_path}: {e}", "danger")
    else:
        custom_print(f"File {file_path} tidak ditemukan.", "warning") # Tidak selalu error, bisa jadi memang tidak dipakai
    
    return "\n".join(captured_output)

def run_login_banner_checks():
    test_name = "Pengecekan Banner Pra-Login"
    print_header(test_name)
    
    results = []
    results.append(capture_banner_file_check("/etc/issue", "login lokal (TTY)"))
    results.append("\n---")
    results.append(capture_banner_file_check("/etc/issue.net", "login jarak jauh (misalnya SSH, Telnet)"))
    
    combined_raw_output = "\n".join(results)
    
    print_info("Rekomendasi Umum: Banner pra-login sebaiknya hanya berisi peringatan hukum yang diperlukan")
    print_info("                 dan HINDARI menampilkan informasi detail tentang sistem (versi OS, kernel, dll.)")

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan banner pra-login."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_login_banner_checks() 