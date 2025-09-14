"""Modul ini bertanggung jawab untuk memeriksa login FTP anonim pada host target.

Ini mencoba untuk terhubung ke server FTP pada port standar (21) dan melakukan
upaya login menggunakan kredensial anonim ('anonymous', 'anonymous@example.com').
Hasilnya menunjukkan apakah login anonim berhasil atau gagal.
"""
import ftplib
import socket
from utils import (
    print_info, print_success, print_warning, print_danger, 
    print_header, send_to_telegram, get_ai_suggestion
)

def capture_ftp_anonymous_check(host):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Mencoba login FTP anonim ke {host}...")
    try:
        ftp = ftplib.FTP(host, timeout=10)
        ftp.login("anonymous", "anonymous@example.com")
        custom_print(f"Login FTP anonim ke {host} BERHASIL.", "success")
        custom_print(f"Server message: {ftp.getwelcome()}", "info")
        try:
            listing = ftp.nlst()
            custom_print(f"Daftar direktori: {listing[:5]}", "info")
        except ftplib.error_perm as e:
            custom_print(f"Tidak dapat membuat daftar direktori setelah login: {e}", "warning")
        ftp.quit()
    except ftplib.error_perm as e:
        custom_print(f"Login FTP anonim ke {host} GAGAL (permission denied): {e}", "warning")
    except (socket.error, ConnectionRefusedError, ConnectionError, OSError) as e:
        custom_print(f"Gagal terhubung ke server FTP {host}: {e}", "danger")
    except (ftplib.error_reply, ftplib.error_temp, ftplib.error_proto) as e:
        custom_print(f"Error komunikasi FTP dengan {host}: {e}", "danger")
    except Exception as e:
        custom_print(f"Error tidak terduga saat mengakses FTP {host}: {e}", "danger")
    
    return "\n".join(captured_output)

def run_ftp_checks(host):
    test_name = f"Pengecekan Login FTP Anonim ({host})"
    print_header(test_name)
    
    raw_output = capture_ftp_anonymous_check(host)
    
    ai_saran = get_ai_suggestion(test_name, raw_output)
    
    send_to_telegram(test_name, raw_output, ai_saran)

if __name__ == '__main__':
    target_host = "localhost"
    run_ftp_checks(target_host) 