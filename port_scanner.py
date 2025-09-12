"""Modul untuk pemindaian port pada host target.

Menyediakan fungsionalitas untuk memeriksa apakah port TCP tertentu terbuka
pada host target dan untuk memindai rentang port untuk menemukan port yang terbuka.
Ini menggunakan koneksi socket dasar untuk menentukan status port.
"""
import socket
import errno
from utils import (
    print_info, print_success, print_warning, print_danger,
    print_header, send_to_telegram, get_gemini_suggestion
)

def capture_check_port_output(host, port):
    captured_output = []
    def custom_print(msg, msg_type="info"):
        captured_output.append(str(msg))
        if msg_type == "info": print_info(msg)
        elif msg_type == "success": print_success(msg)
        elif msg_type == "warning": print_warning(msg)
        elif msg_type == "danger": print_danger(msg)
        else: print(str(msg))

    custom_print(f"Memeriksa port {port} di {host}...", "info")
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            custom_print(f"Port {port} di {host} TERBUKA.", "success")
            
            try:
                service = socket.getservbyport(port, "tcp")
                custom_print(f"Layanan yang umum berjalan di port {port}: {service}", "info")
            except OSError:
                custom_print(f"Tidak dapat menentukan nama layanan umum untuk port {port}.", "info")
        elif result == errno.ECONNREFUSED:
            custom_print(f"Port {port} di {host} TERTUTUP (Connection Refused).", "warning")
        elif result == errno.ETIMEDOUT:
            custom_print(f"Port {port} di {host} TERTUTUP (Timeout).", "warning")
        else:
            error_desc = errno.errorcode.get(result, f"Kode error tidak diketahui: {result}")
            custom_print(f"Port {port} di {host} TERTUTUP atau DIFILTER (Error: {error_desc}).", "warning")
        pass
    except socket.gaierror:
        custom_print(f"Hostname {host} tidak dapat di-resolve.", "danger")
        result = -1
    except socket.error as e:
        custom_print(f"Kesalahan socket saat memeriksa port {port} di {host}: {e}", "danger")
        result = -1
    except Exception as e:
        custom_print(f"Kesalahan tidak terduga saat memeriksa port {port} di {host}: {e}", "danger")
        result = -1
    finally:
        if sock:
            sock.close()

    return "\n".join(captured_output), (result == 0 if 'result' in locals() else False)

def capture_scan_ports_output(host, start_port, end_port):
    captured_output = []
    open_ports_found = []
    def custom_print_scan(msg, msg_type="info"):
        captured_output.append(str(msg))
        
    
    print_info(f"Memulai pemindaian port di {host} dari {start_port} hingga {end_port}...")
    captured_output.append(f"Memulai pemindaian port di {host} dari {start_port} hingga {end_port}...")

    for port in range(start_port, end_port + 1):
        
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                service_name = ""
                try:
                    service_name = f" ({socket.getservbyport(port, 'tcp')})"
                except OSError:
                    pass
                msg = f"Port {port}{service_name} di {host} TERBUKA."
                print_success(msg)
                captured_output.append(msg)
                open_ports_found.append(port)
        except socket.gaierror:
            msg = f"Hostname {host} tidak dapat di-resolve. Batalkan pemindaian."
            print_danger(msg)
            captured_output.append(msg)
            break 
        except socket.error:
            pass
        except Exception as e:
            msg = f"Kesalahan tidak terduga saat memindai port {port} di {host}: {e}"
            print_warning(msg)
            captured_output.append(msg)
        finally:
            if sock:
                sock.close()
    
    if not open_ports_found:
        msg = f"Tidak ada port terbuka yang ditemukan di {host} dalam rentang {start_port}-{end_port}."
        print_info(msg)
        captured_output.append(msg)
    else:
        msg = f"Selesai memindai. Port terbuka yang ditemukan: {open_ports_found}"
        print_success(msg)
        captured_output.append(msg)
        
    return "\n".join(captured_output)

def run_port_scan_checks(host, specific_ports_to_check=None, port_range_to_scan=None):
    test_name = f"Pemindaian Port ({host})"
    print_header(test_name)
    
    all_raw_outputs = []

    if specific_ports_to_check:
        print_info(f"Memeriksa port spesifik: {specific_ports_to_check}")
        for port in specific_ports_to_check:
            output, _ = capture_check_port_output(host, port)
            all_raw_outputs.append(output)
            all_raw_outputs.append("---")
    
    if port_range_to_scan and len(port_range_to_scan) == 2:
        start, end = port_range_to_scan
        if isinstance(start, int) and isinstance(end, int) and start <= end:
            all_raw_outputs.append(capture_scan_ports_output(host, start, end))
        else:
            err_msg = "Rentang port tidak valid. Harap berikan list/tuple dengan dua integer [start, end]."
            print_danger(err_msg)
            all_raw_outputs.append(err_msg)
    
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = f"Tidak ada port terbuka yang terdeteksi atau tidak ada output dari pemindaian port di {host}."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    target = "localhost"

    ports_to_check_individually = [21, 22, 80, 443, 8080]
    run_port_scan_checks(target, 
                         specific_ports_to_check=ports_to_check_individually, 
                         port_range_to_scan=[8000, 8010])