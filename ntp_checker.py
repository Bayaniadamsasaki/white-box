"""Modul untuk memeriksa status sinkronisasi NTP (Network Time Protocol).

Mencoba mendapatkan status NTP menggunakan perintah seperti `timedatectl status`,
`chronyc sources`, dan `ntpq -p`. Keberadaan dan output perintah ini bisa
bervariasi tergantung pada layanan NTP yang digunakan (misalnya, systemd-timesyncd, chrony, ntpd).
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output
)

def run_ntp_checks():
    test_name = "Pemeriksaan Sinkronisasi Waktu (NTP)"
    print_header(test_name)
    all_raw_outputs = []

    ntp_commands = [
        {"desc": "Status timedatectl", "cmd": ["timedatectl", "status"]},
        {"desc": "Sumber Chrony", "cmd": ["chronyc", "sources"]},
        {"desc": "Peer NTPQ", "cmd": ["ntpq", "-p"]} # ntpq sering memerlukan sudo atau user ntp
    ]

    found_authoritative_output = False
    for item in ntp_commands:
        description = item["desc"]
        command_array = item["cmd"]
        
        output_result = capture_command_output(command_array, description)

        is_useful_output = True
        if not output_result or not output_result.strip():
            is_useful_output = False
        elif ("tidak ditemukan" in output_result.lower() or 
              "not found" in output_result.lower() or 
              "could not connect" in output_result.lower() or
              "service is not active" in output_result.lower() or 
              "no such file" in output_result.lower()):
            
            if "timedatectl" in command_array[0]:
                print_warning(f"Perintah '{command_array[0]}' gagal atau layanan tidak aktif. Ini bisa mengindikasikan masalah sinkronisasi waktu.")
            else:
                print_info(f"Perintah '{command_array[0]}' tidak berhasil (mungkin layanan NTP ini tidak digunakan). Mencoba alternatif...")
            is_useful_output = False 

        if is_useful_output:
            all_raw_outputs.append(output_result)

            if "timedatectl" in command_array[0] and "synchronized: yes" in output_result.lower():
                found_authoritative_output = True
                all_raw_outputs.append("Sinkronisasi waktu dikonfirmasi oleh timedatectl.")
                break 
            if "chronyc" in command_array[0] and "^*" in output_result:
                found_authoritative_output = True
                all_raw_outputs.append("Sinkronisasi waktu dikonfirmasi oleh chronyc.")
                break
            all_raw_outputs.append("\n---")
        
    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()

    if not found_authoritative_output and not any(out.strip() for out in all_raw_outputs):
        all_raw_outputs.append("Tidak ada perintah NTP yang berhasil dijalankan atau memberikan output yang menunjukkan status. Periksa konfigurasi NTP secara manual.")
        print_warning("Tidak dapat menentukan status NTP dari perintah yang dicoba.")
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan NTP."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_ntp_checks() 