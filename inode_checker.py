"""Modul untuk memeriksa penggunaan inode pada filesystem.

Menjalankan perintah `df -i` untuk menampilkan penggunaan inode dan memberikan
peringatan jika penggunaan inode pada filesystem tertentu tinggi (misalnya, di atas 80% atau 90%).
Kekurangan inode dapat menyebabkan masalah penulisan file baru meskipun masih ada ruang disk.
"""
import os
import re
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

INODE_USAGE_WARNING_THRESHOLD = 80
INODE_USAGE_CRITICAL_THRESHOLD = 90

def analyze_inode_usage_from_df_output(df_i_raw_output):
    """Menganalisis output mentah dari 'df -i' untuk penggunaan inode yang tinggi.
    Output dari fungsi ini adalah string yang berisi analisis, sudah termasuk print ke konsol.
    """
    analysis_lines = []

    if not df_i_raw_output or not df_i_raw_output.strip() or "tidak ditemukan" in df_i_raw_output.lower() or "not found" in df_i_raw_output.lower():
        return "Analisis penggunaan inode tidak dapat dilakukan karena output 'df -i' tidak valid atau kosong."

    lines = df_i_raw_output.strip().splitlines()
    header_found = False
    high_usage_detected = False

    for line_idx, line_content in enumerate(lines):
        if "Filesystem" in line_content and "IUse%" in line_content:
            header_found = True
            continue
        if not header_found:
            continue

        parts = line_content.split()
        if len(parts) >= 6:
            filesystem = parts[0]
            try:
                iuse_percentage_str = parts[4].rstrip("%")
                iuse_percentage = int(iuse_percentage_str)
                mounted_on = parts[5]
                
                if iuse_percentage >= INODE_USAGE_CRITICAL_THRESHOLD:
                    msg = f"KRITIS: Penggunaan inode di '{filesystem}' ({mounted_on}) sangat tinggi: {iuse_percentage}%"
                    print_danger(msg)
                    analysis_lines.append(msg)
                    high_usage_detected = True
                elif iuse_percentage >= INODE_USAGE_WARNING_THRESHOLD:
                    msg = f"PERINGATAN: Penggunaan inode di '{filesystem}' ({mounted_on}) tinggi: {iuse_percentage}%"
                    print_warning(msg)
                    analysis_lines.append(msg)
                    high_usage_detected = True
            except ValueError:
                w_msg = f"Gagal mem-parse penggunaan inode untuk baris: {line_content}"
                print_warning(w_msg)
                analysis_lines.append(w_msg)
    
    if not header_found:
        w_msg = "Format output 'df -i' tidak dikenali (header tidak ditemukan). Analisis mungkin tidak akurat."
        print_warning(w_msg)
        analysis_lines.append(w_msg)
        return "\n".join(analysis_lines)

    if header_found and not high_usage_detected:
        s_msg = "Penggunaan inode pada semua filesystem yang terpantau berada di bawah ambang batas peringatan."
        print_success(s_msg)
        analysis_lines.append(s_msg)
        
    return "\n".join(analysis_lines)

def run_inode_checks():
    test_name = "Pemeriksaan Penggunaan Inode (df -i)"
    print_header(test_name)
    all_raw_outputs = []

    df_i_output_captured = capture_command_output(["df", "-i"], "Penggunaan Inode Sistem (df -i)")
    
    if df_i_output_captured and df_i_output_captured.strip():
        all_raw_outputs.append(df_i_output_captured)
    else:
        if not df_i_output_captured:
             all_raw_outputs.append("Gagal menjalankan 'df -i' atau perintah tidak menghasilkan output.")

    all_raw_outputs.append("\n--- Hasil Analisis Penggunaan Inode ---")
   
    analysis_report_str = analyze_inode_usage_from_df_output(df_i_output_captured) 
    if analysis_report_str and analysis_report_str.strip():
        all_raw_outputs.append(analysis_report_str)
    else:
        all_raw_outputs.append("Tidak ada analisis spesifik inode yang dihasilkan (mungkin karena error awal atau output kosong dari df -i).")
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan inode."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_inode_checks() 