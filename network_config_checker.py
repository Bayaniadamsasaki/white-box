"""Modul untuk memeriksa konfigurasi jaringan dasar.

Menampilkan informasi antarmuka jaringan (ip addr), tabel routing (ip route),
dan konfigurasi DNS resolver dari /etc/resolv.conf.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output, capture_read_file_content
)

RESOLV_CONF_PATH = "/etc/resolv.conf"

def run_network_config_checks():
    test_name = "Pemeriksaan Konfigurasi Jaringan"
    print_header(test_name)
    all_raw_outputs = []

    tests_definitions = [
        {"desc": "Antarmuka Jaringan (ip addr)", "type": "cmd", "args": ["ip", "addr"]},
        {"desc": "Tabel Routing (ip route)", "type": "cmd", "args": ["ip", "route"]},
        {"desc": f"Konfigurasi DNS Resolver ({RESOLV_CONF_PATH})", "type": "file", "args": RESOLV_CONF_PATH}
    ]

    for test_info in tests_definitions:
        description = test_info["desc"]
        test_type = test_info["type"]
        arguments = test_info["args"]
        
        output_result = ""
        if test_type == "cmd":
            output_result = capture_command_output(arguments, description)
        elif test_type == "file":
            output_result = capture_read_file_content(arguments, description)
        
        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan konfigurasi jaringan."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_network_config_checks() 