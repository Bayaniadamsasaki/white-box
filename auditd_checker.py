"""Modul untuk memeriksa status dan konfigurasi auditd (Linux Audit Daemon).

Memeriksa apakah layanan auditd aktif dan berjalan, serta mencoba menampilkan
daftar aturan audit yang sedang dimuat menggunakan `auditctl -l`.
Memerlukan hak akses root untuk beberapa operasi.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Memeriksa auditd dan aturannya memerlukan hak akses root."

def run_auditd_checks():
    test_name = "Pemeriksaan Audit Daemon (auditd)"
    print_header(test_name)

    if os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []
    tests_definitions = [
        {"desc": "Status Layanan auditd (systemctl is-active)", "type": "cmd", "args": ["sudo", "systemctl", "is-active", "auditd"]},
        {"desc": "Status Detail Layanan auditd (systemctl status)", "type": "cmd", "args": ["sudo", "systemctl", "status", "auditd", "--no-pager"]},
        {"desc": "Daftar Aturan auditd (auditctl -l)", "type": "cmd", "args": ["sudo", "auditctl", "-l"]}
    ]

    for test_info in tests_definitions:
        description = test_info["desc"]
        arguments = test_info["args"]
        output_result = capture_command_output(arguments, description)
        
        if "is-active" in description and output_result:
            if "active" in output_result.lower():
                s_msg = "Layanan auditd terdeteksi aktif."
                print_success(s_msg)
                output_result += f"\n{s_msg}"
            elif "inactive" in output_result.lower() or "failed" in output_result.lower():
                d_msg = "PERINGATAN: Layanan auditd tidak aktif atau dalam status gagal!"
                print_danger(d_msg)
                output_result += f"\n{d_msg}"
            elif "not found" in output_result.lower() or "tidak ditemukan" in output_result.lower():
                w_msg = "Layanan auditd (atau systemctl) tidak ditemukan. Auditd mungkin tidak terinstal."
                print_warning(w_msg)
                output_result += f"\n{w_msg}"
        
        if "auditctl -l" in description and output_result:
            if "No rules" in output_result or "LIST_RULES: Aucun message" in output_result: # Pesan "Aucun message" untuk locale Prancis
                w_msg = "Tidak ada aturan audit yang dimuat. Ini adalah konfigurasi yang lemah."
                print_warning(w_msg)
                output_result += f"\n{w_msg}"
            elif "AUDIT_STATUS: enabled=0" in output_result:
                d_msg = "Auditd dilaporkan tidak diaktifkan (enabled=0) dalam status aturan!"
                print_danger(d_msg)
                output_result += f"\n{d_msg}"
            elif "LIST_RULES: list of rules" in output_result or (os.geteuid() == 0 and not "No rules" in output_result and not "enabled=0" in output_result and len(output_result.splitlines()) > 3) : # Heuristik ada aturan jika output > 3 baris sbg root
                s_msg = "Aturan auditd terdeteksi. Periksa secara manual untuk kelengkapan."
                print_success(s_msg)
                output_result += f"\n{s_msg}"

        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan auditd."
        if os.geteuid() != 0:
            combined_raw_output += f" {REQUIRED_ROOT_MESSAGE}"
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_auditd_checks() 