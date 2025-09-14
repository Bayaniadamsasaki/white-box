"""Modul ini bertanggung jawab untuk memeriksa layanan web pada URL target.

Ini melakukan permintaan HTTP GET ke URL yang diberikan untuk memeriksa apakah
layanan web responsif dan mengidentifikasi header Server jika ada.
Juga melakukan pemeriksaan dasar untuk file umum seperti robots.txt dan sitemap.xml.
"""
import requests
from urllib.parse import urljoin
from utils import (
    print_info, print_success, print_warning, print_danger,
    print_header, send_to_telegram, get_ai_suggestion
)

def capture_web_service_check(base_url):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Memeriksa layanan web di {base_url}...", "info")
    
    if not base_url.startswith(("http://", "https://")):
        custom_print(f"URL tidak memiliki skema (http/https), mencoba dengan http://", "warning")
        base_url = "http://" + base_url
        custom_print(f"URL yang digunakan: {base_url}", "info")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(base_url, headers=headers, timeout=10, allow_redirects=True)
        custom_print(f"Status code untuk {base_url}: {response.status_code}", "success" if response.ok else "warning")
        
        server_header = response.headers.get("Server")
        if server_header:
            custom_print(f"Header Server: {server_header}", "info")
            if any(ver in server_header.lower() for ver in ["apache", "nginx", "iis", "litespeed"]):
                 custom_print(f"Teknologi server umum terdeteksi: {server_header}.", "info")
            if any(char.isdigit() for char in server_header) and len(server_header) > 5: # heuristik sederhana
                custom_print(f"Header server '{server_header}' mungkin mengungkapkan versi detail. Pertimbangkan untuk menyembunyikannya.", "warning")
        else:
            custom_print("Header Server tidak ditemukan.", "info")
        
        common_files = ["robots.txt", "sitemap.xml"]
        for f_path in common_files:
            file_url = urljoin(base_url, f_path)
            try:
                file_res = requests.get(file_url, headers=headers, timeout=5)
                if file_res.ok:
                    custom_print(f"File {f_path} ditemukan di {file_url} (Status: {file_res.status_code})", "success")
                else:
                    custom_print(f"File {f_path} tidak ditemukan atau tidak dapat diakses di {file_url} (Status: {file_res.status_code})", "info")
            except requests.exceptions.RequestException as fe:
                custom_print(f"Gagal memeriksa {file_url}: {fe}", "warning")

    except requests.exceptions.Timeout:
        custom_print(f"Timeout saat mencoba terhubung ke {base_url}.", "danger")
    except requests.exceptions.ConnectionError:
        custom_print(f"Gagal terhubung ke {base_url}. Pastikan URL benar dan server berjalan.", "danger")
    except requests.exceptions.RequestException as e:
        custom_print(f"Kesalahan saat memeriksa layanan web di {base_url}: {e}", "danger")
    
    return "\n".join(captured_output)

def run_web_checks(url):
    test_name = f"Pengecekan Layanan Web ({url})"
    print_header(test_name)
    
    raw_output = capture_web_service_check(url)
    
    ai_saran = get_ai_suggestion(test_name, raw_output)

    send_to_telegram(test_name, raw_output, ai_saran)

if __name__ == '__main__':
    target_url = "http://localhost" 
    run_web_checks(target_url) 