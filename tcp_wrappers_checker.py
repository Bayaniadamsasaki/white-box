"""Modul ini bertanggung jawab untuk memeriksa konfigurasi TCP Wrappers.

TCP Wrappers (/etc/hosts.allow dan /etc/hosts.deny) adalah mekanisme kontrol
akses jaringan yang lebih tua. Meskipun firewall modern lebih umum digunakan,
file-file ini masih bisa relevan jika dikonfigurasi. Modul ini membaca
dan menampilkan isi file-file tersebut.
"""
import os
from utils import (print_info, print_success, print_warning,
                   print_danger, print_header, send_to_telegram,
                   get_ai_suggestion)

def capture_tcp_wrapper_config_check(file_path):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(msg)
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(msg)

    custom_print(f"Membaca file konfigurasi TCP Wrappers: {file_path}...", "info")
    if os.path.exists(file_path):
        try:
            
            if not os.access(file_path, os.R_OK) and os.geteuid() != 0:
                 custom_print(f"Tidak ada izin baca untuk {file_path} sebagai pengguna biasa. Hasil mungkin tidak akurat.", "warning")
            
            with open(file_path, "r") as f:
                content = f.read().strip()
                if content:
                    custom_print(f"Isi {file_path}:", "success")
                    
                    print(content) 
                    captured_output.append(content)

                    if file_path == "/etc/hosts.deny" and "ALL: ALL" in content.replace(" ", ""):
                        custom_print("Konfigurasi umum yang ketat ('ALL: ALL') ditemukan di hosts.deny.", "success")
                    elif file_path == "/etc/hosts.allow" and not content.strip():
                        custom_print("hosts.allow kosong, yang berarti semua akses di-defer ke hosts.deny (jika hosts.deny dikonfigurasi untuk memblokir).", "info")
                else:
                    custom_print(f"File {file_path} kosong.", "info")
        except Exception as e:
            custom_print(f"Gagal membaca {file_path}: {e}", "danger")
    else:
        custom_print(f"File {file_path} tidak ditemukan. TCP Wrappers mungkin tidak digunakan atau dikonfigurasi melalui file ini.", "warning")
    
    return "\n".join(captured_output)

def run_tcp_wrappers_checks():
    test_name = "Pengecekan Konfigurasi TCP Wrappers"
    print_header(test_name)
    
    print_info("Catatan: TCP Wrappers adalah mekanisme kontrol akses jaringan yang lebih tua.")
    print_info("         Firewall modern (iptables, ufw, nftables) seringkali menjadi metode utama.")
    print_info("         Namun, jika dikonfigurasi, file ini tetap relevan.")
    if not os.geteuid() == 0:
        print_warning("Peringatan: Membaca file konfigurasi ini mungkin memerlukan hak root jika permission-nya ketat.")
    
    results = []
    results.append(capture_tcp_wrapper_config_check("/etc/hosts.allow"))
    results.append("\n---")
    results.append(capture_tcp_wrapper_config_check("/etc/hosts.deny"))
    
    combined_raw_output = "\n".join(results)

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan TCP Wrappers."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_tcp_wrappers_checks() 