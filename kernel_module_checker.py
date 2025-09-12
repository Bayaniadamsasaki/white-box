"""Modul untuk memeriksa modul kernel yang sedang dimuat (loaded) pada sistem.

Menggunakan perintah `lsmod` untuk menampilkan daftar modul kernel, ukurannya,
dan modul lain yang bergantung padanya. Ini penting untuk keamanan karena modul kernel
berjalan dengan hak akses tertinggi dan bisa menjadi target serangan jika memiliki celah
atau jika ada modul berbahaya yang dimuat.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

def run_kernel_module_checks():
    """Menjalankan pemeriksaan terkait modul kernel yang dimuat."""
    test_name = "Pemeriksaan Modul Kernel (lsmod)"
    print_header(test_name)
    all_raw_outputs = []
    unwanted_modules = []  # Definisikan unwanted_modules di sini

    lsmod_output = capture_command_output(["lsmod"], "Daftar Modul Kernel yang Dimuat")
    
    if lsmod_output and lsmod_output.strip():
        all_raw_outputs.append(lsmod_output)
        if "Module" in lsmod_output and "Size" in lsmod_output and "Used by" in lsmod_output:
            print_success("Berhasil mendapatkan daftar modul kernel.")
           
            for mod in unwanted_modules:
                if mod in lsmod_output:
                    print_warning(f"Modul '{mod}' ditemukan. Pertimbangkan untuk menonaktifkannya jika tidak diperlukan.")
        else:
            print_warning("Output 'lsmod' tidak memiliki header yang diharapkan. Pemeriksaan manual mungkin diperlukan.")
    else:
        msg = "Gagal menjalankan 'lsmod' atau perintah tidak menghasilkan output."
        all_raw_outputs.append(msg)
        print_warning(msg)

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan modul kernel (lsmod)."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_kernel_module_checks() 