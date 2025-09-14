"""Modul untuk memeriksa perangkat USB yang terhubung ke server.

Menggunakan perintah `lsusb` untuk menampilkan daftar perangkat USB. Ini bisa membantu
dalam audit keamanan fisik dan mengidentifikasi perangkat yang tidak sah atau tidak dikenal
yang terhubung ke sistem, yang bisa menjadi risiko keamanan.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output
)

def run_usb_devices_checks():
    """Menjalankan pemeriksaan terkait perangkat USB yang terhubung."""
    test_name = "Pemeriksaan Perangkat USB (lsusb)"
    print_header(test_name)
    all_raw_outputs = []
    
    lsusb_output = capture_command_output(["lsusb"], "Daftar Perangkat USB yang Terhubung")
    
    if lsusb_output and lsusb_output.strip():
        all_raw_outputs.append(lsusb_output)
        # Heuristik sederhana untuk output normal lsusb
        if "Bus" in lsusb_output and "Device" in lsusb_output and "ID" in lsusb_output:
            print_success("Berhasil mendapatkan daftar perangkat USB.")
            # Analisis tambahan:
            if len(lsusb_output.strip().splitlines()) > 1:
                print_warning("Perangkat USB terdeteksi. Pastikan semua perangkat yang terhubung sah dan diperlukan.")
            else:
                print_success("Tidak ada perangkat USB eksternal yang terdeteksi (selain mungkin hub root).")
        elif "unable to initialize libusb" in lsusb_output.lower() or "cannot open" in lsusb_output.lower():
             print_danger("Gagal menginisialisasi libusb atau mengakses perangkat USB. Periksa izin atau instalasi libusb.")
        else:
            print_warning("Output 'lsusb' tidak memiliki header yang diharapkan atau tampak kosong. Pemeriksaan manual mungkin diperlukan.")
    else:
        msg = "Gagal menjalankan 'lsusb' atau perintah tidak menghasilkan output (mungkin tidak terinstal atau tidak ada perangkat USB)."
        # Periksa apakah lsusb ada
        check_lsusb_exists = capture_command_output(["which", "lsusb"], "Pengecekan keberadaan lsusb")
        if "tidak ditemukan" in check_lsusb_exists.lower() or "not found" in check_lsusb_exists.lower():
            msg = "Perintah 'lsusb' tidak ditemukan. Paket usbutils mungkin perlu diinstal."
        all_raw_outputs.append(msg)
        print_warning(msg)

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan perangkat USB (lsusb)."
        print_info(combined_raw_output)

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_usb_devices_checks() 