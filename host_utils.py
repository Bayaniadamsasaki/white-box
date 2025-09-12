"""Modul utilitas host untuk melakukan resolusi nama host dan tes ping.

Fungsi-fungsi dalam modul ini membantu memverifikasi konektivitas dasar
dan ketersediaan host target dengan mencoba mengubah nama host menjadi alamat IP
dan mengirimkan paket ICMP Echo Request (ping).
"""
import socket
import subprocess
import platform
from utils import (
    print_info, print_success, print_warning, print_danger,
    print_header, send_to_telegram, get_gemini_suggestion
)

def capture_resolve_host_output(hostname):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Mencoba me-resolve hostname: {hostname}...", "info")
    try:
        ip_address = socket.gethostbyname(hostname)
        custom_print(f"Hostname {hostname} berhasil di-resolve ke alamat IP: {ip_address}", "success")
    except socket.gaierror as e:
        custom_print(f"Gagal me-resolve hostname {hostname}: {e}", "danger")
    except Exception as e:
        custom_print(f"Kesalahan tidak terduga saat me-resolve {hostname}: {e}", "danger")
    return "\n".join(captured_output)

def capture_ping_host_output(hostname, count=1):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Melakukan ping ke {hostname} ({count} kali)...", "info")
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), hostname]
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=15) # Timeout 15 detik untuk proses ping
        
        if process.returncode == 0:
            custom_print(f"Ping ke {hostname} BERHASIL.", "success")
            if stdout:
                custom_print("Output Ping:", "info")
                for line in stdout.splitlines():
                    print(f"    {line}")
                    captured_output.append(f"    {line}")
            if captured_output and captured_output[-1] == "Output Ping:": captured_output.pop()
            if captured_output and stdout.splitlines() and captured_output[-len(stdout.splitlines())] == "Output Ping:":
                 pass

        else:
            custom_print(f"Ping ke {hostname} GAGAL (return code: {process.returncode}).", "danger")
            if stdout:
                custom_print("Output Ping (stdout):")
                for line in stdout.splitlines(): print(f"    {line}"); captured_output.append(f"    {line}")
            if stderr:
                custom_print("Error Ping (stderr):", "warning")
                for line in stderr.splitlines(): print(f"    {line}"); captured_output.append(f"    {line}")

    except subprocess.TimeoutExpired:
        custom_print(f"Timeout saat melakukan ping ke {hostname}. Perintah dibatalkan.", "danger")
    except FileNotFoundError:
        custom_print("Perintah 'ping' tidak ditemukan. Pastikan sudah terinstal dan ada di PATH.", "danger")
    except Exception as e:
        custom_print(f"Kesalahan tidak terduga saat melakukan ping ke {hostname}: {e}", "danger")
        
    return "\n".join(list(dict.fromkeys(captured_output)))

def run_host_utils_checks(target_host, ping_count=1):
    test_name = f"Utilitas Host ({target_host})"
    print_header(test_name)
    
    output_parts = []
    output_parts.append(capture_resolve_host_output(target_host))
    output_parts.append("\n---")
    output_parts.append(capture_ping_host_output(target_host, ping_count))
    
    combined_raw_output = "\n".join(output_parts)
    
    if not combined_raw_output.strip():
        combined_raw_output = f"Tidak ada output yang dihasilkan dari pemeriksaan utilitas host untuk {target_host}."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

def resolve_host(hostname):
    """Resolve hostname to IP address and return the IP"""
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return None
    except Exception:
        return None

def ping_host(hostname, count=1):
    """Ping a host and return True if successful"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), hostname]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

if __name__ == '__main__':
    host_to_test = "localhost"
    
    run_host_utils_checks(host_to_test, ping_count=2) 