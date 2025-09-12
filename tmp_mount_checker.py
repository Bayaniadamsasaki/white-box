"""Modul untuk memeriksa opsi pemasangan (mount options) untuk direktori /tmp.

Direktori /tmp yang tidak dipasang dengan opsi keamanan yang tepat (seperti noexec,
nodev, nosuid) dapat menjadi vektor serangan. Modul ini memeriksa opsi pemasangan
/tmp menggunakan `findmnt` atau parsing output `mount`.
"""
import os
import re
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

RECOMMENDED_TMP_OPTIONS = ["noexec", "nosuid", "nodev"]

def analyze_tmp_mount_options(mount_output_str):
    """Menganalisis output perintah mount untuk opsi /tmp."""
    analysis_lines = []
    tmp_mounted_separately = False
    current_options = []

    if not mount_output_str or not mount_output_str.strip():
        analysis_lines.append("Output perintah mount kosong atau tidak valid.")
        return "\n".join(analysis_lines), False

    if "TARGET=/tmp" in mount_output_str or "/tmp" in mount_output_str:
        
        lines = mount_output_str.strip().splitlines()
        for line in lines:
            
            is_findmnt_direct_output = not (" on " in line and " type " in line) and all(opt.isalnum() or opt in [",", "-"] for opt in line.split(","))

            if is_findmnt_direct_output:
                current_options = [opt.strip() for opt in line.split(',')]
                tmp_mounted_separately = True
                analysis_lines.append(f"Opsi pemasangan /tmp (dari findmnt): {', '.join(current_options)}")
                break 
            elif " /tmp " in line:
                tmp_mounted_separately = True
                match = re.search(r'\((.*?)\)', line)
                if match:
                    current_options = [opt.strip() for opt in match.group(1).split(',')]
                    analysis_lines.append(f"Opsi pemasangan /tmp (dari mount): {', '.join(current_options)}")
                else:
                    analysis_lines.append(f"Tidak dapat mem-parse opsi untuk /tmp dari baris: {line}")
                break
    
    if not tmp_mounted_separately:
        
        note = "/tmp tidak terlihat dipasang sebagai partisi terpisah. Ia mungkin mewarisi opsi dari partisi root (/). Pemeriksaan opsi root diperlukan untuk analisis lengkap."
        print_info(note)
        analysis_lines.append(note)
       
        return "\n".join(analysis_lines), True

    missing_options = []
    present_options_str = ", ".join(current_options)
    if not current_options:
        warn_msg = "/tmp terpasang terpisah tetapi tidak ada opsi pemasangan yang terdeteksi. Ini tidak biasa."
        print_warning(warn_msg)
        analysis_lines.append(warn_msg)
        missing_options.extend(RECOMMENDED_TMP_OPTIONS)
    else:
        for opt in RECOMMENDED_TMP_OPTIONS:
            if opt not in current_options:
                missing_options.append(opt)

    if missing_options:
        warn_msg = f"PERINGATAN: /tmp dipasang dengan opsi: [{present_options_str}]. Opsi keamanan yang direkomendasikan hilang: {', '.join(missing_options)}."
        print_danger(warn_msg)
        analysis_lines.append(warn_msg)
    else:
        succ_msg = f"GOOD: /tmp dipasang dengan opsi keamanan yang direkomendasikan ({present_options_str})."
        print_success(succ_msg)
        analysis_lines.append(succ_msg)
        
    return "\n".join(analysis_lines), True

def run_tmp_mount_checks():
    """Menjalankan pemeriksaan terkait opsi pemasangan /tmp."""
    test_name = "Pemeriksaan Opsi Pemasangan /tmp"
    print_header(test_name)
    all_raw_outputs = []
    analysis_reports = []

    findmnt_command = ["findmnt", "-n", "-o", "OPTIONS", "/tmp"]
    findmnt_output = capture_command_output(findmnt_command, "Opsi Pemasangan /tmp (via findmnt)")
    
    tmp_options_analyzed = False
    raw_mount_data_for_analysis = ""

    if findmnt_output and ("tidak ditemukan" not in findmnt_output.lower() and "not found" not in findmnt_output.lower()) and findmnt_output.strip():
        all_raw_outputs.append(findmnt_output)
        raw_mount_data_for_analysis = findmnt_output
        analysis_text, analyzed_successfully = analyze_tmp_mount_options(findmnt_output)
        if analyzed_successfully:
            analysis_reports.append(analysis_text)
            tmp_options_analyzed = True
    else:

        print_info("Perintah 'findmnt' untuk /tmp gagal atau tidak ditemukan. Mencoba dengan 'mount | grep /tmp' (parsing internal).")
        all_raw_outputs.append("Fallback: Hasil 'findmnt' tidak valid, menggunakan output dari 'mount'.")
        
        mount_full_output = capture_command_output(["mount"], "Output Perintah mount (penuh)")
        if mount_full_output and mount_full_output.strip():
            all_raw_outputs.append(mount_full_output)

            tmp_lines = [line for line in mount_full_output.splitlines() if " /tmp " in line]
            if tmp_lines:
                raw_mount_data_for_analysis = "\n".join(tmp_lines)
                analysis_text, analyzed_successfully = analyze_tmp_mount_options(raw_mount_data_for_analysis)
                if analyzed_successfully:
                    analysis_reports.append(analysis_text)
                    tmp_options_analyzed = True
            else:

                analysis_text, _ = analyze_tmp_mount_options("")
                analysis_reports.append(analysis_text)
                tmp_options_analyzed = True
        else:
            err_msg = "Gagal menjalankan perintah 'mount' atau tidak ada output."
            print_danger(err_msg)
            all_raw_outputs.append(err_msg)

    if not tmp_options_analyzed:
        warn_msg = "Tidak dapat menganalisis opsi pemasangan /tmp secara otomatis dari output yang tersedia."
        print_warning(warn_msg)
        analysis_reports.append(warn_msg)
    
    
    if analysis_reports:
        all_raw_outputs.append("\n--- Hasil Analisis Opsi Pemasangan /tmp ---")
        all_raw_outputs.extend(analysis_reports)

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan mount /tmp dan /var/tmp."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_tmp_mount_checks() 