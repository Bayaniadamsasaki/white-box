"""Modul untuk memeriksa variabel lingkungan sistem.

Memeriksa variabel PATH untuk entri yang tidak aman (seperti direktori saat ini '.'
atau string kosong '') dan menampilkan variabel lingkungan root jika dijalankan sebagai root.
"""
import os
import platform
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output # Untuk `env` jika diperlukan
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Melihat variabel lingkungan root memerlukan hak akses root."

def check_path_variable():
    """Menganalisis variabel PATH untuk entri yang tidak aman."""
    captured_lines = ["Menganalisis variabel PATH..."]
    print_info(captured_lines[0])
    insecure_entries = []
    path_var = os.getenv("PATH")
    
    if path_var:
        paths = path_var.split(os.pathsep)
        captured_lines.append(f"PATH: {path_var}")
        print_info(f"PATH: {path_var}")
        for p_entry in paths:
            if p_entry == "" or p_entry == ".":
                insecure_entries.append(p_entry if p_entry else "'' (empty string)")
        
        if insecure_entries:
            msg = f"Ditemukan entri PATH yang tidak aman: {', '.join(insecure_entries)}. Ini bisa menjadi risiko keamanan."
            print_danger(msg)
            captured_lines.append(msg)
        else:
            msg = "Tidak ada entri PATH yang jelas tidak aman ('.' atau '') ditemukan."
            print_success(msg)
            captured_lines.append(msg)
    else:
        msg = "Variabel PATH tidak ditemukan."
        print_warning(msg)
        captured_lines.append(msg)
    return "\n".join(list(dict.fromkeys(captured_lines)))

def run_environment_checks():
    test_name = "Pemeriksaan Variabel Lingkungan"
    print_header(test_name)
    all_raw_outputs = []

    path_analysis_output = check_path_variable()
    if path_analysis_output and path_analysis_output.strip():
        all_raw_outputs.append(path_analysis_output)
        all_raw_outputs.append("\n---")

    root_env_desc = "Variabel Lingkungan Root"
    
    # Check for Windows - different privilege check
    if platform.system() == "Windows":
        # On Windows, we can't easily check for Administrator privileges
        print_info("Menampilkan variabel lingkungan sistem (Windows)...")
        root_env_output = capture_command_output(["set"], root_env_desc + " (Windows)")
        if root_env_output and root_env_output.strip():
            all_raw_outputs.append(root_env_output)
            all_raw_outputs.append("\n---")
    elif hasattr(os, 'geteuid') and os.geteuid() == 0:
        print_info(f"Menampilkan variabel lingkungan untuk root (karena dijalankan sebagai root)...")
        root_env_output = capture_command_output(["env"], root_env_desc)
        if root_env_output and root_env_output.strip():
            all_raw_outputs.append(root_env_output)
            all_raw_outputs.append("\n---")
    else:
        msg = f"Tidak dijalankan sebagai root. {root_env_desc} tidak ditampilkan."
        print_info(msg)
        all_raw_outputs.append(msg)
        all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan environment."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_environment_checks() 