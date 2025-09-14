"""Modul untuk melakukan berbagai pemeriksaan yang memerlukan hak akses root.

Termasuk pemeriksaan status UFW, aturan iptables, proses root, file SUID/SGID,
kemampuan sudo tanpa password, layanan yang berjalan sebagai root, port yang listening,
dan perizinan file-file sistem penting.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output, capture_read_file_content
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Beberapa atau semua pemeriksaan dalam modul ini memerlukan hak akses root untuk hasil yang akurat."

def run_root_checks():
    test_name = "Pemeriksaan Spesifik Root"
    print_header(test_name)

    if os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)
        

    all_raw_outputs = []

    tests_definitions = [
        {"desc": "Status UFW", "type": "cmd", "args": ["sudo", "ufw", "status"]},
        {"desc": "Aturan iptables (filter)", "type": "cmd", "args": ["sudo", "iptables", "-L", "-v", "-n", "--line-numbers"]},
        {"desc": "Aturan iptables (nat)", "type": "cmd", "args": ["sudo", "iptables", "-t", "nat", "-L", "-v", "-n", "--line-numbers"]},
        {"desc": "Aturan iptables (mangle)", "type": "cmd", "args": ["sudo", "iptables", "-t", "mangle", "-L", "-v", "-n", "--line-numbers"]},
        {"desc": "Proses yang berjalan sebagai root (top 10 memori)", "type": "cmd", "args": "ps aux --sort=-pmem | awk '$1==\"root\"' | head", "shell": True},
        {"desc": "Layanan yang berjalan sebagai root (top 10 CPU)", "type": "cmd", "args": "ps aux --sort=-pcpu | awk '$1==\"root\" && $11 !~ /^\\[/' | head", "shell": True},
        {"desc": "File SUID", "type": "cmd", "args": ["sudo", "find", "/", "-xdev", "-type", "f", "-perm", "/4000", "-print0"]},
        {"desc": "File SGID", "type": "cmd", "args": ["sudo", "find", "/", "-xdev", "-type", "f", "-perm", "/2000", "-print0"]},
        {"desc": "Pemeriksaan /etc/sudoers dan /etc/sudoers.d untuk NOPASSWD", "type": "cmd", "args": ["sudo", "grep", "-rE", "NOPASSWD", "/etc/sudoers", "/etc/sudoers.d/"]},
        {"desc": "Port TCP yang Mendengarkan (ss)", "type": "cmd", "args": ["sudo", "ss", "-tulnp"]},
        {"desc": "Izin /etc/shadow", "type": "cmd", "args": ["sudo", "ls", "-l", "/etc/shadow"]},
        {"desc": "Izin /etc/passwd", "type": "cmd", "args": ["sudo", "ls", "-l", "/etc/passwd"]},
        {"desc": "Izin Direktori /root", "type": "cmd", "args": ["sudo", "ls", "-ld", "/root"]}
    ]

    for test_info in tests_definitions:
        description = test_info["desc"]
        test_type = test_info["type"]
        arguments = test_info["args"]
        use_shell = test_info.get("shell", False)
        
        output_result = ""
        if test_type == "cmd":
            output_result = capture_command_output(arguments, description, shell=use_shell)
        elif test_type == "file":
            output_result = capture_read_file_content(arguments, description)
        
        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        if os.geteuid() != 0:
            msg = f"{REQUIRED_ROOT_MESSAGE}\nTidak ada output yang dihasilkan, kemungkinan besar karena kurangnya hak akses root."
            print_warning(msg)
            combined_raw_output = msg
        else:
            msg = "Tidak ada output yang dihasilkan dari pemeriksaan root meskipun dijalankan sebagai root."
            print_warning(msg)
            combined_raw_output = msg

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    
    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    print_info("Menjalankan pemeriksaan root. Pastikan skrip dijalankan dengan sudo untuk hasil yang komprehensif.")
    run_root_checks() 