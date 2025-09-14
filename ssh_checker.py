"""Modul ini bertanggung jawab untuk mengambil banner SSH dari host dan port target.

Banner SSH seringkali mengungkapkan versi perangkat lunak SSH yang digunakan,
yang bisa menjadi informasi berharga bagi penyerang jika ada kerentanan
yang diketahui untuk versi tersebut. Modul ini mencoba terhubung ke port SSH
dan membaca banner awal yang dikirim oleh server.
"""
import socket
from utils import (
    print_info, print_success, print_warning, print_danger,
    print_header, send_to_telegram, get_ai_suggestion
)

def capture_ssh_banner_grab(host, port=22):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Mencoba mengambil banner SSH dari {host}:{port}...", "info")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        banner = sock.recv(1024).decode(errors='ignore').strip()
        sock.close()
        if banner:
            custom_print(f"Banner SSH dari {host}:{port}: {banner}", "success")
            
            if "openssh" in banner.lower():
                custom_print(f"Server SSH tampaknya menjalankan OpenSSH.", "info")
            if len(banner.split('\n')) > 1:
                 custom_print(f"Banner terdiri dari beberapa baris.", "info")
        else:
            custom_print(f"Tidak ada banner yang diterima dari {host}:{port} atau banner kosong.", "warning")
    except socket.timeout:
        custom_print(f"Timeout saat mencoba terhubung ke {host}:{port} untuk banner SSH.", "danger")
    except socket.error as e:
        custom_print(f"Kesalahan socket saat mencoba mengambil banner SSH dari {host}:{port}: {e}", "danger")
    except Exception as e:
        custom_print(f"Kesalahan tidak terduga saat mengambil banner SSH dari {host}:{port}: {e}", "danger")
    
    return "\n".join(captured_output)

def run_ssh_banner_checks(host, port=22):
    test_name = f"Pengecekan Banner SSH ({host}:{port})"
    print_header(test_name)
    
    raw_output = capture_ssh_banner_grab(host, port)
    
    ai_saran = get_ai_suggestion(test_name, raw_output)
    
    
    send_to_telegram(test_name, raw_output, ai_saran)

if __name__ == '__main__':
    target_host = "localhost" 
    target_port = 22
    
    run_ssh_banner_checks(target_host, target_port) 