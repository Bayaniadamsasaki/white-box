"""Modul untuk memeriksa status modul keamanan Linux seperti AppArmor dan SELinux.

Menjalankan perintah sistem untuk mendapatkan status AppArmor (aa-status)
dan status SELinux (sestatus).
"""
import os
import subprocess
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Pemeriksaan modul keamanan mungkin memerlukan hak akses root untuk detail penuh."

def run_security_module_checks():
    test_name = "Pemeriksaan Modul Keamanan (AppArmor, SELinux)"
    print_header(test_name)

    if os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []

    tests_definitions = [
        {"desc": "Status AppArmor (aa-status)", "type": "cmd", "args": ["sudo", "aa-status"]},
        {"desc": "Status SELinux (sestatus)", "type": "cmd", "args": ["sestatus"]} # sestatus biasanya tidak perlu sudo
    ]

    for test_info in tests_definitions:
        description = test_info["desc"]
        arguments = test_info["args"]
        output_result = capture_command_output(arguments, description)
        
        if "tidak ditemukan" in output_result.lower() or "not found" in output_result.lower():
            if "aa-status" in description.lower():
                msg = "AppArmor tampaknya tidak terinstal atau perintah aa-status tidak ada di PATH."
                print_warning(msg)
                output_result += f"\n{msg}"
            elif "sestatus" in description.lower():
                msg = "SELinux tampaknya tidak aktif/terinstal atau perintah sestatus tidak ada di PATH."
                print_warning(msg)
                output_result += f"\n{msg}"

        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan modul keamanan."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_security_module_checks() 