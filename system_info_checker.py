"""Modul untuk mengumpulkan informasi sistem dasar.

Fungsi-fungsi dalam modul ini menjalankan perintah sistem umum untuk mendapatkan
detail seperti versi kernel, informasi rilis OS, penggunaan disk, penggunaan memori,
dan beban CPU rata-rata. Ini berguna untuk mendapatkan gambaran umum konfigurasi sistem.
Output dari setiap perintah ditangkap untuk pelaporan.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger,
    print_header, send_to_telegram, get_ai_suggestion,
    capture_command_output, capture_read_file_content
)

def run_system_info_checks():
    test_name = "Pengumpulan Informasi Sistem Dasar"
    print_header(test_name)
    
    all_raw_outputs = []

    tests_to_run = [
        ("Versi Kernel", "cmd", ["uname", "-r"]),
        ("Informasi Rilis OS", "file", "/etc/os-release"),
        ("Penggunaan Disk", "cmd", ["df", "-h"]),
        ("Penggunaan Memori", "cmd", ["free", "-m"]),
        ("Beban CPU Rata-rata", "cmd", ["uptime"])
    ]

    for description, test_type, arg in tests_to_run:
        output_result = ""
        if test_type == "cmd":
            output_result = capture_command_output(arg, description)
        elif test_type == "file":
            output_result = capture_read_file_content(arg, description)
        
        if output_result:
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")
        
    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = f"Tidak ada informasi sistem yang berhasil dikumpulkan."
        print_warning(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    
    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_system_info_checks() 