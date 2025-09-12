"""Modul untuk memeriksa pembaruan paket yang tertunda.

Menggunakan manajer paket sistem (apt untuk Debian/Ubuntu) untuk menampilkan
daftar paket yang dapat ditingkatkan.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)


def run_package_manager_checks():
    test_name = "Pemeriksaan Pembaruan Paket (apt)"
    print_header(test_name)
    all_raw_outputs = []

    
    print_info("Mencoba mendapatkan daftar paket yang dapat diupgrade (apt list --upgradable).")
    print_warning("Catatan: Untuk hasil yang paling akurat, jalankan 'sudo apt update' secara manual sebelum skrip ini.")

    tests_definitions = [
        {"desc": "Paket yang Dapat Diupgrade (apt)", "type": "cmd", "args": ["apt", "list", "--upgradable"]}
    ]

    for test_info in tests_definitions:
        description = test_info["desc"]
        arguments = test_info["args"]
        output_result = capture_command_output(arguments, description)
        
        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan package manager."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_package_manager_checks() 