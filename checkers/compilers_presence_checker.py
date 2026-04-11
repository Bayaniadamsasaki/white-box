"""Modul untuk memeriksa keberadaan kompiler umum dan alat build pada sistem.

Keberadaan kompiler (seperti gcc, g++, clang) dan alat build (seperti make, cmake)
di server produksi dapat meningkatkan risiko keamanan. Jika penyerang mendapatkan
akses, mereka dapat menggunakannya untuk mengkompilasi dan menjalankan kode berbahaya.
Modul ini memeriksa keberadaan beberapa kompiler dan alat build umum menggunakan `which`.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output
)

TOOLS_TO_CHECK = [
    "gcc", "g++", "clang", "clang++", "cc", 
    "make", "cmake", "ninja",
    "javac", "go", "rustc", "python", "perl", "ruby",
]

def run_compilers_presence_checks():
    """Menjalankan pemeriksaan keberadaan kompiler dan alat build."""
    test_name = "Pemeriksaan Keberadaan Kompiler dan Alat Build"
    print_header(test_name)
    all_raw_outputs = []
    found_tools_summary = []
    not_found_count = 0

    print_info(f"Memeriksa keberadaan alat berikut: {', '.join(TOOLS_TO_CHECK)}")

    for tool in TOOLS_TO_CHECK:
        raw_which_output = capture_command_output(["which", tool], f"Pengecekan Keberadaan: {tool}", suppress_output=True)
        all_raw_outputs.append(f"--- Hasil 'which {tool}' ---\n{raw_which_output}\n---")

        if raw_which_output and ("tidak ditemukan" not in raw_which_output.lower() and "not found" not in raw_which_output.lower()) and tool in raw_which_output:
            path = raw_which_output.strip().splitlines()[-1]
            msg = f"DITEMUKAN: Alat '{tool}' ditemukan di: {path}"
            print_warning(msg)
            found_tools_summary.append(msg)
        else:
            not_found_count +=1
    
    if found_tools_summary:
        all_raw_outputs.append("\n--- Ringkasan Alat yang Ditemukan ---")
        all_raw_outputs.extend(found_tools_summary)
        warning_message = "PERINGATAN: Satu atau lebih kompiler/alat build ditemukan di sistem. Ini bisa menjadi risiko keamanan di server produksi. Pertimbangkan untuk menghapusnya jika tidak benar-benar diperlukan."
        print_danger(warning_message)
        all_raw_outputs.append(f"\n{warning_message}")
    else:
        success_message = "GOOD: Tidak ada kompiler atau alat build umum yang terdeteksi dari daftar yang diperiksa."
        print_success(success_message)
        all_raw_outputs.append(f"\n{success_message}")
    
    print_info(f"Total alat dari daftar yang tidak ditemukan: {not_found_count}/{len(TOOLS_TO_CHECK)}")
    all_raw_outputs.append(f"Total alat dari daftar yang tidak ditemukan: {not_found_count}/{len(TOOLS_TO_CHECK)}")

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan keberadaan kompiler."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_compilers_presence_checks() 