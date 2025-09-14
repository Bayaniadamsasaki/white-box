"""Modul untuk memeriksa konfigurasi kebijakan kata sandi sistem.

Membaca dan menganalisis file /etc/login.defs untuk parameter kebijakan kata sandi
penting seperti PASS_MAX_DAYS, PASS_MIN_DAYS, PASS_WARN_AGE, dan ENCRYPT_METHOD.
Memberikan rekomendasi berdasarkan praktik terbaik umum.
"""
import os
import re
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_read_file_content
)

LOGIN_DEFS_PATH = "/etc/login.defs"

def analyze_login_defs_content(raw_content):
    """Menganalisis konten /etc/login.defs untuk kebijakan kata sandi."""
    analysis_lines = []
    recommendations = []
    found_settings = {}

    if not raw_content or not raw_content.strip():
        analysis_lines.append("Konten /etc/login.defs kosong atau tidak dapat dibaca.")
        return "\n".join(analysis_lines)

    policy_params_to_check = {
        "PASS_MAX_DAYS":    {"check_type": "max", "value": 90, "warn_if_missing": True, "unit": "hari", "desc": "Maksimum umur password"},
        "PASS_MIN_DAYS":    {"check_type": "min", "value": 7,  "warn_if_missing": True, "unit": "hari", "desc": "Minimum umur password"},
        "PASS_WARN_AGE":    {"check_type": "min", "value": 14, "warn_if_missing": True, "unit": "hari", "desc": "Peringatan kadaluarsa password"},
        "ENCRYPT_METHOD":   {"check_type": "strength", "preferred": ["SHA512", "YESCRYPT"], "acceptable": ["SHA256"], "weak":["MD5", "DES"], "desc": "Metode Enkripsi Password"},
        "LOGIN_TIMEOUT":    {"check_type": "max", "value": 60, "warn_if_missing": False, "unit": "detik", "desc": "Timeout login"},
        "UID_MIN":          {"check_type": "min", "value": 1000, "warn_if_missing": False, "unit": "kali", "desc": "UID minimum untuk user biasa"},
        "GID_MIN":          {"check_type": "min", "value": 1000, "warn_if_missing": False, "unit": "kali", "desc": "GID minimum untuk grup biasa"},
        "UID_MAX":          {"check_type": "max", "value": 60000, "warn_if_missing": False, "unit": "kali", "desc": "UID maksimum untuk user biasa"},
        "GID_MAX":          {"check_type": "max", "value": 60000, "warn_if_missing": False, "unit": "kali", "desc": "GID maksimum untuk grup biasa"},
        "LOGIN_TIMEOUT":    {"check_type": "max", "value": 60, "warn_if_missing": False, "unit": "detik", "desc": "Timeout login"},
        "LOGIN_RETRIES":    {"check_type": "max", "value": 5,  "warn_if_missing": False, "unit": "kali", "desc": "Maksimum percobaan login"},
        "FAIL_DELAY":       {"check_type": "min", "value": 3,  "warn_if_missing": False, "unit": "detik", "desc": "Delay setelah login gagal"},
    }

    for line in raw_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        parts = re.split(r'\s+', line, 1)
        if len(parts) == 2:
            key, value = parts[0], parts[1]
            found_settings[key] = value

            if key in policy_params_to_check:
                param_policy = policy_params_to_check[key]
                current_value_str = value
                unit = param_policy.get("unit", "")
                desc = param_policy.get("desc", key)

                if param_policy["check_type"] in ["min", "max"]:
                    try:
                        current_value_int = int(current_value_str)
                        expected_value = param_policy["value"]
                        if param_policy["check_type"] == "max" and current_value_int > expected_value:
                            recommendations.append(f"{desc} ('{key}') saat ini '{current_value_int} {unit}', direkomendasikan <= '{expected_value} {unit}'.")
                        elif param_policy["check_type"] == "min" and current_value_int < expected_value:
                            recommendations.append(f"{desc} ('{key}') saat ini '{current_value_int} {unit}', direkomendasikan >= '{expected_value} {unit}'.")
                        else:
                            analysis_lines.append(f"[+] Pengaturan OK: {desc} ('{key}') = {current_value_int} {unit}.")
                    except ValueError:
                        analysis_lines.append(f"[!] Peringatan: Nilai untuk '{key}' ('{current_value_str}') bukan angka yang valid.")
                
                elif param_policy["check_type"] == "strength" and key == "ENCRYPT_METHOD":
                    if current_value_str.upper() in param_policy["preferred"]:
                        analysis_lines.append(f"[+] Pengaturan OK: {desc} ('{key}') menggunakan metode kuat: {current_value_str}.")
                    elif current_value_str.upper() in param_policy["acceptable"]:
                        analysis_lines.append(f"[*] Catatan: {desc} ('{key}') menggunakan metode {current_value_str}. Pertimbangkan {param_policy['preferred']}.")
                    elif current_value_str.upper() in param_policy["weak"]:
                        recommendations.append(f"{desc} ('{key}') menggunakan metode lemah: {current_value_str}! Sangat disarankan menggunakan {param_policy['preferred']}.")
                    else:
                        analysis_lines.append(f"[!] {desc} ('{key}') menggunakan metode: {current_value_str}. Pastikan ini adalah metode enkripsi yang kuat dan modern.")
    
    for key, param_policy in policy_params_to_check.items():
        if param_policy.get("warn_if_missing", False) and key not in found_settings:
            recommendations.append(f"Parameter '{key}' ({param_policy.get('desc', key)}) tidak ditemukan di {LOGIN_DEFS_PATH}. Pertimbangkan untuk mengaturnya.")

    if recommendations:
        analysis_lines.append("\nRekomendasi Kebijakan Kata Sandi:")
        for rec in recommendations:
            print_warning(rec)
            
            analysis_lines.append(f"- {rec}")
    else:
        
        if any(key in found_settings for key in policy_params_to_check):
            s_msg = "Konfigurasi kebijakan kata sandi di /etc/login.defs tampak sesuai dengan pemeriksaan dasar."
            print_success(s_msg)
            analysis_lines.append(s_msg)
        elif not found_settings:
             analysis_lines.append("Tidak ada pengaturan yang dapat diperiksa di /etc/login.defs atau file kosong.")

    return "\n".join(analysis_lines)

def run_password_policy_checks():
    test_name = f"Pemeriksaan Kebijakan Kata Sandi ({LOGIN_DEFS_PATH})"
    print_header(test_name)
    all_raw_outputs = []

    login_defs_raw_content = capture_read_file_content(LOGIN_DEFS_PATH, "File Kebijakan Login")
    
    if login_defs_raw_content and login_defs_raw_content.strip():
        all_raw_outputs.append(login_defs_raw_content)
        all_raw_outputs.append("\n--- Analisis Kebijakan Kata Sandi ---")
        
        raw_text_for_analysis = ""
        if os.path.exists(LOGIN_DEFS_PATH):
            try:
                with open(LOGIN_DEFS_PATH, "r") as f_login_defs:
                    raw_text_for_analysis = f_login_defs.read()
            except Exception as e:
                err_msg = f"Gagal membaca konten mentah {LOGIN_DEFS_PATH} untuk analisis: {e}"
                print_danger(err_msg)
                all_raw_outputs.append(err_msg)

        if raw_text_for_analysis:
            analysis_result_str = analyze_login_defs_content(raw_text_for_analysis)
            if analysis_result_str and analysis_result_str.strip():
                
                all_raw_outputs.append(analysis_result_str)
        else:
            all_raw_outputs.append(f"Tidak dapat melakukan analisis mendalam karena konten mentah {LOGIN_DEFS_PATH} tidak dapat diakses.")
    else:
        all_raw_outputs.append(f"Tidak dapat membaca atau konten {LOGIN_DEFS_PATH} kosong.")

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan kebijakan password."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_password_policy_checks() 