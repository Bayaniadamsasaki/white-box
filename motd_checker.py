"""Modul untuk memeriksa konten Message of the Day (MOTD).

Memeriksa file MOTD statis (biasanya `/etc/motd`), file MOTD dinamis
(seringkali `/run/motd.dynamic` atau dihasilkan oleh skrip di `/etc/update-motd.d/`).
MOTD dapat berisi informasi sensitif atau menyesatkan jika tidak dikelola dengan baik.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_read_file_content, capture_command_output
)

MOTD_STATIC_PATH = "/etc/motd"
MOTD_DYNAMIC_PATH = "/run/motd.dynamic"
MOTD_UPDATE_DIR = "/etc/update-motd.d"

def run_motd_checks():
    """Menjalankan pemeriksaan terkait Message of the Day (MOTD)."""
    test_name = "Pemeriksaan Message of the Day (MOTD)"
    print_header(test_name)
    all_raw_outputs = []
    analysis_notes = []
    static_motd_details = capture_read_file_content(MOTD_STATIC_PATH, f"Pemeriksaan Konten MOTD Statis ({MOTD_STATIC_PATH})")
    all_raw_outputs.append(static_motd_details)

    actual_content_static = ""
    if MOTD_STATIC_PATH in static_motd_details and "Konten File:" in static_motd_details:
        try:
            actual_content_static = static_motd_details.split("Konten File:", 1)[1].strip()
        except IndexError:
            actual_content_static = ""
    
    if actual_content_static:
        if "unauthorized access" not in actual_content_static.lower() and \
           "authorised access" not in actual_content_static.lower() and \
           "authorized access" not in actual_content_static.lower():
            note = f"Peringatan: {MOTD_STATIC_PATH} mungkin tidak berisi pesan peringatan akses tidak sah yang jelas."
            print_warning(note)
            analysis_notes.append(note)
        else:
            s_note = f"{MOTD_STATIC_PATH} tampaknya berisi semacam peringatan akses."
            print_success(s_note)
            analysis_notes.append(s_note)
    elif "tidak ditemukan" in static_motd_details.lower() or "tidak dapat diakses" in static_motd_details.lower() or "cannot open" in static_motd_details.lower():
        i_note = f"{MOTD_STATIC_PATH} tidak ditemukan atau tidak dapat diakses."
        print_info(i_note)
        analysis_notes.append(i_note)

    all_raw_outputs.append("\n--- Pemeriksaan MOTD Dinamis ---")
    dynamic_motd_details = capture_read_file_content(MOTD_DYNAMIC_PATH, f"Pemeriksaan Konten MOTD Dinamis ({MOTD_DYNAMIC_PATH})")
    all_raw_outputs.append(dynamic_motd_details)
    update_motd_dir_listing = capture_command_output(["ls", "-lA", MOTD_UPDATE_DIR], f"Pemeriksaan Direktori Skrip MOTD ({MOTD_UPDATE_DIR})")
    all_raw_outputs.append(update_motd_dir_listing)
    if MOTD_UPDATE_DIR in update_motd_dir_listing and ("total 0" == update_motd_dir_listing.strip().splitlines()[-1].strip() and len(update_motd_dir_listing.strip().splitlines()) == 1):
        note = f"Direktori {MOTD_UPDATE_DIR} kosong atau hanya berisi header."
        print_info(note)
        analysis_notes.append(note)
    elif os.path.isdir(MOTD_UPDATE_DIR) and not os.listdir(MOTD_UPDATE_DIR):
        note = f"Direktori {MOTD_UPDATE_DIR} ada tapi kosong."
        print_info(note)
        analysis_notes.append(note)
    elif "tidak ditemukan" in update_motd_dir_listing.lower() or "No such file or directory" in update_motd_dir_listing:
        note = f"Direktori {MOTD_UPDATE_DIR} tidak ditemukan."
        print_info(note)
        analysis_notes.append(note)
    elif MOTD_UPDATE_DIR in update_motd_dir_listing: # Jika ada listing
        s_note = f"Skrip di {MOTD_UPDATE_DIR} ditemukan. Periksa output di atas untuk detail."
        print_success(s_note)
        analysis_notes.append(s_note)

    if analysis_notes:
        all_raw_outputs.append("\n--- Catatan Analisis MOTD ---")
        all_raw_outputs.extend(analysis_notes)
    
    general_recommendation = "Rekomendasi Umum MOTD: Pastikan MOTD berisi banner peringatan hukum yang sesuai, tidak mengungkapkan versi software atau informasi sensitif internal secara berlebihan, dan semua skrip di /etc/update-motd.d/ telah diaudit keamanannya."
    print_info(general_recommendation)
    all_raw_outputs.append(f"\n{general_recommendation}")

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan MOTD."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_motd_checks() 