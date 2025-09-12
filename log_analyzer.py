"""Modul untuk menganalisis file log untuk entri yang mencurigakan.

Ini memeriksa upaya sudo terbaru, upaya login yang gagal, dan pesan error/peringatan
dari dmesg dengan menjalankan perintah sistem yang relevan (grep, dmesg, tail).
Membutuhkan hak akses root untuk membaca beberapa file log.
"""
import subprocess
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output 
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Membaca beberapa file log memerlukan hak akses root."

AUTH_LOG_PATHS = ["/var/log/auth.log", "/var/log/secure"]
DMESG_LEVELS = "err,crit,alert,emerg,warn"

def get_existing_log_paths(paths):
    """Mengembalikan path pertama yang ada dari daftar, atau None."""
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def run_log_analyzer_checks():
    test_name = "Analisis File Log"
    print_header(test_name)

    if os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []
    tests_definitions = []

    auth_log = get_existing_log_paths(AUTH_LOG_PATHS)
    if auth_log:
       
        tests_definitions.append({
            "desc": f"Upaya Sudo Terbaru (dari {auth_log}, maks 50 baris terakhir)", 
            "type": "cmd", 
            "args": ["sudo", "grep", "-i", "sudo:", auth_log, "|", "tail", "-n", "50"]
        })
    else:
        msg = f"Tidak ditemukan file log otentikasi umum ({AUTH_LOG_PATHS}). Lewati cek upaya sudo."
        print_warning(msg)
        all_raw_outputs.append(msg)

    
    if auth_log:
        grep_pattern = 'failed password|authentication failure|invalid user'        
        tests_definitions.append({
            "desc": f"Upaya Login Gagal (dari {auth_log}, maks 50 baris terakhir)", 
            "type": "cmd", 
            "args": ["sudo", "grep", "-Eia", grep_pattern, auth_log, "|", "tail", "-n", "50"]
        })
    else:
        msg = f"Tidak ditemukan file log otentikasi umum ({AUTH_LOG_PATHS}). Lewati cek upaya login gagal."
        print_warning(msg)
        all_raw_outputs.append(msg)
    
    tests_definitions.append({
        "desc": f"Pesan dmesg (level: {DMESG_LEVELS}, maks 50 baris terakhir)", 
        "type": "cmd", 
        "args": ["sudo", "dmesg", f"--level={DMESG_LEVELS}", "|", "tail", "-n", "50"]
    })

    for test_info in tests_definitions:
        description = test_info["desc"]
        arguments = test_info["args"]
        
        is_piped_command = False
        if "|" in arguments:
            is_piped_command = True
            command_str = " ".join(arguments)
            print_info(f"Menjalankan perintah shell: {command_str}")
            captured_output_lines = [f"Menjalankan tes: {description} (Perintah: '{command_str}')"]
            try:
                result = subprocess.run(command_str, shell=True, capture_output=True, text=True, check=False, timeout=20)
                if result.returncode == 0:
                    msg_success = f"Output untuk '{description}':"
                    print_success(msg_success)
                    captured_output_lines.append(msg_success)
                    if result.stdout and result.stdout.strip():
                        for line in result.stdout.strip().splitlines():
                            print(f"    {line}")
                            captured_output_lines.append(f"    {line}")
                    else:
                        captured_output_lines.append("    (Tidak ada output standar)")
                else:
                    msg_fail = f"Perintah '{description}' gagal dengan kode: {result.returncode}"
                    print_danger(msg_fail)
                    captured_output_lines.append(msg_fail)
                    if result.stdout and result.stdout.strip(): captured_output_lines.append(f"    Output standar: {result.stdout.strip()}")
                    if result.stderr and result.stderr.strip(): captured_output_lines.append(f"    Output error: {result.stderr.strip()}")
                output_result = "\n".join(captured_output_lines)
            except Exception as e:
                output_result = f"Kesalahan saat menjalankan perintah shell untuk {description}: {e}"
                print_danger(output_result)
        else:
            output_result = capture_command_output(arguments, description)
        
        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output signifikan dari analisis log."
        if os.geteuid() != 0:
            combined_raw_output += f" {REQUIRED_ROOT_MESSAGE}"
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_log_analyzer_checks() 