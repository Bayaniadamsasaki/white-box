"""Modul untuk memeriksa batas sumber daya (ulimits) sistem.

Menampilkan ulimits saat ini untuk proses yang menjalankan skrip (menggunakan perintah ulimit -a)
dan mencoba membaca file konfigurasi batas sistem global seperti /etc/security/limits.conf
serta file-file di /etc/security/limits.d/.
"""
import subprocess
import os
import glob
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output, capture_read_file_content
)

LIMITS_CONF_PATH = "/etc/security/limits.conf"
LIMITS_D_PATH = "/etc/security/limits.d"

def show_current_ulimits():
    print("[*] Menampilkan batas sumber daya (ulimit -a) untuk proses saat ini...")
    try:
        
        result = subprocess.run("ulimit -a", shell=True, capture_output=True, text=True, check=True)
        print("[+] Batas ulimit saat ini:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[-] Gagal menjalankan 'ulimit -a': {e.stderr}")
    except Exception as e:
        print(f"[-] Gagal mendapatkan info ulimit: {e}")

def check_system_wide_limits_conf():
    print("[*] Memeriksa konfigurasi batas sumber daya sistem (/etc/security/limits.conf dan /etc/security/limits.d/)...")
    files_to_check = ["/etc/security/limits.conf"]
    
    if os.path.isdir("/etc/security/limits.d"):
        files_in_dir = glob.glob(os.path.join("/etc/security/limits.d/", "*.conf"))
        files_to_check.extend(files_in_dir)

    found_config = False
    for conf_file in files_to_check:
        if os.path.exists(conf_file):
            found_config = True
            print(f"\n    --- Isi {conf_file} ---")
            try:
                with open(conf_file, "r") as f:
                    has_content = False
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            print(f"        {line}")
                            has_content = True
                    if not has_content:
                        print("        (Tidak ada konfigurasi aktif)")
            except Exception as e:
                print(f"        [-] Gagal membaca {conf_file}: {e}")
            
    if not found_config and not files_to_check:
        print("    [-] Tidak ada file konfigurasi limits.conf atau limits.d/*.conf yang ditemukan.")
    elif not found_config and files_to_check == ["/etc/security/limits.conf"] and not os.path.exists(files_to_check[0]):
        print(f"    [-] File {files_to_check[0]} tidak ditemukan.")


def run_resource_limit_checks():
    test_name = "Pemeriksaan Batas Sumber Daya (ulimits)"
    print_header(test_name)
    all_raw_outputs = []

    
    ulimit_desc = "Ulimits Saat Ini (ulimit -a)"
    ulimit_cmd_str = "ulimit -a"
    print_info(f"Menjalankan tes: {ulimit_desc} (Perintah: '{ulimit_cmd_str}')")
    captured_ulimit_lines = [f"Menjalankan tes: {ulimit_desc} (Perintah: '{ulimit_cmd_str}')"]
    try:
        
        result = subprocess.run(ulimit_cmd_str, shell=True, capture_output=True, text=True, check=False, timeout=10)
        if result.returncode == 0:
            msg_success = f"Output untuk '{ulimit_desc}':"
            print_success(msg_success)
            captured_ulimit_lines.append(msg_success)
            if result.stdout and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    print(f"    {line}")
                    captured_ulimit_lines.append(f"    {line}")
            else:
                captured_ulimit_lines.append("    (Tidak ada output standar dari ulimit -a)")
        else:
            msg_fail = f"Perintah '{ulimit_desc}' gagal dengan kode: {result.returncode}"
            print_danger(msg_fail)
            captured_ulimit_lines.append(msg_fail)
            if result.stdout and result.stdout.strip(): captured_ulimit_lines.append(f"    Output standar: {result.stdout.strip()}")
            if result.stderr and result.stderr.strip(): captured_ulimit_lines.append(f"    Output error: {result.stderr.strip()}")
        all_raw_outputs.append("\n".join(list(dict.fromkeys(captured_ulimit_lines))))
        all_raw_outputs.append("\n---")
    except Exception as e:
        err_msg = f"Kesalahan saat menjalankan '{ulimit_cmd_str}': {e}"
        print_danger(err_msg)
        all_raw_outputs.append(err_msg)
        all_raw_outputs.append("\n---")


    output_limits_conf = capture_read_file_content(LIMITS_CONF_PATH, f"File Konfigurasi Batas Global ({LIMITS_CONF_PATH})")
    if output_limits_conf and output_limits_conf.strip():
        all_raw_outputs.append(output_limits_conf)
        all_raw_outputs.append("\n---")


    print_info(f"Membaca file konfigurasi di direktori: {LIMITS_D_PATH}")
    if os.path.exists(LIMITS_D_PATH) and os.path.isdir(LIMITS_D_PATH):
        try:
            limits_d_files_found = False
            for item_name in sorted(os.listdir(LIMITS_D_PATH)):
                item_path = os.path.join(LIMITS_D_PATH, item_name)
                
                if os.path.isfile(item_path) and not os.path.islink(item_path):
                    limits_d_files_found = True
                    file_desc = f"File Konfigurasi Batas Tambahan ({item_path})"
                    file_content_out = capture_read_file_content(item_path, file_desc)
                    if file_content_out and file_content_out.strip():
                        all_raw_outputs.append(file_content_out)
                        all_raw_outputs.append("\n---") 
            if not limits_d_files_found:
                msg_info = f"Tidak ada file konfigurasi yang ditemukan di {LIMITS_D_PATH}."
                print_info(msg_info)
                all_raw_outputs.append(msg_info)
                all_raw_outputs.append("\n---")

        except Exception as e:
            err_msg = f"Gagal memproses direktori {LIMITS_D_PATH}: {e}"
            print_danger(err_msg)
            all_raw_outputs.append(err_msg)
            all_raw_outputs.append("\n---")
    else:
        msg_warn = f"Direktori {LIMITS_D_PATH} tidak ditemukan atau bukan direktori."
        print_warning(msg_warn)
        all_raw_outputs.append(msg_warn)
        all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan batas sumber daya."
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)
    

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_resource_limit_checks() 