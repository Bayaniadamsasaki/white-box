"""Modul untuk memeriksa segmen memori bersama (shared memory segments) pada sistem.

Menggunakan perintah `ipcs -m` untuk menampilkan daftar segmen memori bersama,
ukurannya, dan pemiliknya. Ini bisa berguna untuk mengidentifikasi penggunaan memori
oleh aplikasi atau potensi kebocoran sumber daya.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output
)

def run_shared_memory_checks():
    """Menjalankan pemeriksaan terkait segmen memori bersama."""
    test_name = "Pemeriksaan Segmen Memori Bersama (ipcs -m)"
    print_header(test_name)
    all_raw_outputs = []

    ipcs_output = capture_command_output(["ipcs", "-m"], "Daftar Segmen Memori Bersama")
    
    if ipcs_output and ipcs_output.strip():
        all_raw_outputs.append(ipcs_output)
        if "0x00000000" not in ipcs_output and "key" not in ipcs_output.lower() and len(ipcs_output.splitlines()) < 3:
             print_warning("Output 'ipcs -m' tampak tidak biasa atau kosong. Pastikan perintah berjalan dengan benar.")
        elif len(ipcs_output.splitlines()) > 3 :
             print_success("Berhasil mendapatkan daftar segmen memori bersama.")
    else:
        
        msg = "Gagal menjalankan 'ipcs -m' atau perintah tidak menghasilkan output."
        all_raw_outputs.append(msg)
        print_warning(msg)

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan shared memory."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_shared_memory_checks() 