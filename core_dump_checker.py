"""Modul untuk memeriksa konfigurasi dan keberadaan core dumps.

Core dumps adalah file yang berisi snapshot memori dari suatu proses pada saat
terjadi crash. Meskipun berguna untuk debugging, core dumps dapat berisi data sensitif
(seperti kunci, password, dll.). Modul ini memeriksa pengaturan core dump
(misalnya, melalui `ulimit -c` atau `/etc/security/limits.conf` secara tidak langsung,
konfigurasi systemd coredump, atau `/proc/sys/kernel/core_pattern`)
dan mencari file core dump yang ada.
"""
import subprocess
import os
import glob
import re
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output, capture_read_file_content
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Beberapa pemeriksaan core dump mungkin memerlukan hak akses root untuk detail penuh."


CORE_DUMP_PATHS_TO_CHECK = ["/var/crash/", "/var/lib/systemd/coredump/", "/tmp/", "./"] # Tambahkan path lain jika perlu
SYSCTL_CORE_PATTERN = "kernel.core_pattern"
SYSCTL_CORE_USES_PID = "kernel.core_uses_pid"

def check_suid_dumpable():
    print("[*] Memeriksa kernel parameter fs.suid_dumpable...")
    try:
        result = subprocess.run(['sysctl', 'fs.suid_dumpable'], capture_output=True, text=True)
        if result.returncode == 0:
            current_value = result.stdout.strip().split("=")[1].strip()
            if current_value == "0":
                print(f"[+] fs.suid_dumpable sudah diset ke 0 (aman). ({result.stdout.strip()})")
            else:
                print(f"[!] Rekomendasi: Set 'fs.suid_dumpable' ke '0' untuk mencegah SUID process core dumps yang bisa membocorkan info. Saat ini: '{current_value}'")
        else:
            print(f"[-] Tidak dapat membaca parameter kernel 'fs.suid_dumpable': {result.stderr.strip()}")
    except FileNotFoundError:
        print("[-] Perintah 'sysctl' tidak ditemukan.")
    except Exception as e:
        print(f"[-] Gagal mengecek fs.suid_dumpable: {e}")

def check_core_pattern():
    print("\n[*] Memeriksa pola nama file core dump (/proc/sys/kernel/core_pattern)...")
    core_pattern_file = "/proc/sys/kernel/core_pattern"
    try:
        with open(core_pattern_file, "r") as f:
            pattern = f.read().strip()
            print(f"[+] Pola core dump saat ini: '{pattern}'")
            if pattern.startswith("|"):
                print("    [+] Core dump diarahkan ke program eksternal. Pastikan program tersebut aman dan dikonfigurasi dengan benar.")
                if "systemd-coredump" in pattern:
                    print("    [+] Core dump ditangani oleh systemd-coredump.")
            elif not os.path.isabs(pattern.split()[0]): # Jika tidak piped dan path tidak absolut
                print("[!] Peringatan: Pola core dump tidak menggunakan path absolut. Core dump bisa ditulis ke direktori kerja proses yang crash.")
                print("    Rekomendasi: Gunakan path absolut untuk core_pattern atau arahkan ke systemd-coredump.")
            else:
                print("    [+] Pola core dump menggunakan path absolut.")
    except FileNotFoundError:
        print(f"[-] File '{core_pattern_file}' tidak ditemukan.")
    except Exception as e:
        print(f"[-] Gagal membaca {core_pattern_file}: {e}")

def check_existing_core_dumps():
    print("\n[*] Memeriksa keberadaan file core dump lama...")
    common_locations = [
        "/var/lib/systemd/coredump/", # Systemd
        "/var/crash/",                # Apport atau crash lainnya
        "/var/spool/abrt/",           # ABRT (RHEL/Fedora)
        "./"
        "/tmp/", # Temp dir
        "/var/tmp/", # Temp dir
        "/home/", # Home dir
        "/root/", # Root home dir
        "/usr/local/", # Local dir
        "/usr/lib/", # Lib dir
        "/usr/share/", # Share dir

    ]
    found_any = False
    for loc in common_locations:
        if os.path.isdir(loc):
            print(f"    Mencari di {loc}...")
            try:
                core_files = [f for f in glob.glob(os.path.join(loc, "*")) if os.path.isfile(f) and os.path.getsize(f) > 0]
                if core_files:
                    found_any = True
                    print(f"[!] Ditemukan file yang mungkin core dump di {loc}:")
                    for core_file in core_files[:5]:
                        print(f"        - {core_file} (Size: {os.path.getsize(core_file)} bytes)")
                    if len(core_files) > 5:
                        print(f"        (... dan {len(core_files) - 5} file lainnya)")
                    print("    Rekomendasi: Periksa file-file ini dan hapus jika tidak lagi diperlukan. Core dump bisa berisi data sensitif.")
            except Exception as e:
                print(f"    [-] Gagal mencari di {loc}: {e}")
    
    if not found_any:
        print("[+] Tidak ada file core dump yang jelas ditemukan di lokasi umum yang diperiksa.")

def run_core_dump_checks():
    """Menjalankan pemeriksaan terkait core dumps."""
    test_name = "Pemeriksaan Core Dump"
    print_header(test_name)
    all_raw_outputs = []
    analysis_notes = []

    ulimit_note = "Pemeriksaan 'ulimit -c' (ukuran maksimum file core dump):\n"
    try:
        process = os.popen("ulimit -Sc")
        ulimit_c_output = process.read().strip()
        process.close()
        if ulimit_c_output:
            ulimit_note += f"  Soft limit saat ini untuk ukuran file core (ulimit -Sc): {ulimit_c_output}\n"
            if ulimit_c_output == "0":
                s_msg = "  Ukuran file core dump dibatasi ke 0 (core dumps dinonaktifkan oleh soft ulimit ini). Ini umumnya baik untuk server produksi."
                print_success(s_msg)
                ulimit_note += s_msg + "\n"
            elif ulimit_c_output == "unlimited":
                w_msg = "  PERINGATAN: Ukuran file core dump tidak terbatas (unlimited). Core dump besar dapat memenuhi disk."
                print_warning(w_msg)
                ulimit_note += w_msg + "\n"
            else:
                i_msg = f"  Ukuran file core dump adalah {ulimit_c_output}. Pastikan ini sesuai kebijakan."
                print_info(i_msg)
                ulimit_note += i_msg + "\n"
        else:
            ulimit_note += "  Tidak dapat mengambil output 'ulimit -Sc'.\n"
    except Exception as e:
        ulimit_note += f"  Gagal menjalankan 'ulimit -Sc': {e}\n"
    all_raw_outputs.append(ulimit_note)
    analysis_notes.append(ulimit_note.split("\n",1)[1] if "\n" in ulimit_note else ulimit_note) # Ambil detailnya saja

    core_pattern_output = capture_command_output(["sysctl", SYSCTL_CORE_PATTERN], f"Pola Nama File Core Dump ({SYSCTL_CORE_PATTERN})")
    all_raw_outputs.append(core_pattern_output)
    if SYSCTL_CORE_PATTERN in core_pattern_output:
        pattern_value = core_pattern_output.split("=")[-1].strip()
        analysis_notes.append(f"Pola nama file core dump ({SYSCTL_CORE_PATTERN}): {pattern_value}")
        if "|/bin/false" in pattern_value or "|/usr/bin/false" in pattern_value:
            s_msg = f"  Core dump diarahkan ke /bin/false, efektif menonaktifkannya melalui sysctl. Ini baik."
            print_success(s_msg)
            analysis_notes.append(s_msg)
        elif pattern_value == "core":
            w_msg = f"  PERINGATAN: {SYSCTL_CORE_PATTERN} adalah 'core'. Ini akan membuat file bernama 'core' di direktori kerja proses, yang mungkin dapat ditulis oleh pengguna."
            print_warning(w_msg)
            analysis_notes.append(w_msg)
        elif pattern_value.startswith("|"):
            i_msg = f"  Core dump diarahkan ke program eksternal: {pattern_value}. Pastikan program ini aman dan terkonfigurasi dengan benar."
            print_info(i_msg)
            analysis_notes.append(i_msg)
        else:
            i_msg = f"  Core dump disimpan sesuai pola: {pattern_value}. Periksa direktori target untuk keamanan dan ruang disk."
            print_info(i_msg)
            analysis_notes.append(i_msg)

    core_uses_pid_output = capture_command_output(["sysctl", SYSCTL_CORE_USES_PID], f"Penggunaan PID pada Nama File Core ({SYSCTL_CORE_USES_PID})")
    all_raw_outputs.append(core_uses_pid_output)
    if SYSCTL_CORE_USES_PID in core_uses_pid_output:
        pid_value = core_uses_pid_output.split("=")[-1].strip()
        analysis_notes.append(f"Penggunaan PID di nama file core ({SYSCTL_CORE_USES_PID}): {pid_value}")
        if pid_value == "0":
            w_msg = f"  PERINGATAN: {SYSCTL_CORE_USES_PID} adalah 0. Ini dapat menyebabkan file core saling menimpa jika pola tidak unik."
            print_warning(w_msg)
            analysis_notes.append(w_msg)
        else:
            s_msg = f"  {SYSCTL_CORE_USES_PID} adalah 1. PID akan ditambahkan ke nama file core, membantu mencegah penimpaan."
            print_success(s_msg)
            analysis_notes.append(s_msg)

    limits_conf_path = "/etc/security/limits.conf"
    limits_d_path = "/etc/security/limits.d/"
    all_raw_outputs.append(f"\n--- Pemeriksaan {limits_conf_path} dan {limits_d_path} untuk 'core' limit ---")
    limits_content = capture_read_file_content(limits_conf_path, f"Konten {limits_conf_path}")
    all_raw_outputs.append(limits_content)
    found_core_limit_in_files = False
    if limits_content and "tidak ditemukan" not in limits_content.lower():
        for line in limits_content.splitlines():
            if not line.strip().startswith("#") and "core" in line:
                analysis_notes.append(f"Potensi batasan core di {limits_conf_path}: {line.strip()}")
                print_info(f"Potensi batasan core di {limits_conf_path}: {line.strip()}")
                found_core_limit_in_files = True
    
    if os.path.isdir(limits_d_path):
        try:
            for entry in os.listdir(limits_d_path):
                file_path = os.path.join(limits_d_path, entry)
                if os.path.isfile(file_path) and entry.endswith(".conf"):
                    content = capture_read_file_content(file_path, f"Konten {file_path}")
                    all_raw_outputs.append(content)
                    if content and "tidak ditemukan" not in content.lower():
                        for line in content.splitlines():
                            if not line.strip().startswith("#") and "core" in line:
                                analysis_notes.append(f"Potensi batasan core di {file_path}: {line.strip()}")
                                print_info(f"Potensi batasan core di {file_path}: {line.strip()}")
                                found_core_limit_in_files = True
        except Exception as e:
            err_msg = f"Gagal membaca direktori {limits_d_path}: {e}"
            print_warning(err_msg)
            all_raw_outputs.append(err_msg)
    
    if not found_core_limit_in_files:
        analysis_notes.append(f"Tidak ada batasan 'core' eksplisit yang ditemukan di {limits_conf_path} atau file di {limits_d_path}.")
    else:
        analysis_notes.append("Periksa batasan core di atas untuk memastikan nilainya '0' untuk menonaktifkan, atau nilai aman lainnya.")

    all_raw_outputs.append("\n--- Pencarian File Core Dump yang Ada ---")
    analysis_notes.append("\nPencarian File Core Dump yang Ada:")
    found_core_files_summary = []
    for path_to_check in CORE_DUMP_PATHS_TO_CHECK:
        common_patterns = ["core", "core.*", "*.core"]
        if os.path.isdir(path_to_check):
            print_info(f"Mencari file core di direktori: {path_to_check}...")
            found_in_path = False
            for pattern in common_patterns:
                try:
                    core_files = glob.glob(os.path.join(path_to_check, pattern))
                    for core_file in core_files:
                        try:
                            stat_info = os.stat(core_file)
                            file_size_mb = stat_info.st_size / (1024 * 1024)
                            msg = f"  DITEMUKAN: File core dump potensial: {core_file} (Ukuran: {file_size_mb:.2f} MB)"
                            print_danger(msg)
                            found_core_files_summary.append(msg)
                            found_in_path = True
                        except Exception as e_stat:
                            er_msg = f"  Tidak dapat mengambil stat untuk {core_file}: {e_stat}"
                            print_warning(er_msg)
                            found_core_files_summary.append(er_msg)
                except Exception as e_glob:
                    print_warning(f"  Gagal melakukan glob di {path_to_check} dengan pola {pattern}: {e_glob}")            
            if not found_in_path:
                s_msg = f"  Tidak ada file core dump umum yang ditemukan di {path_to_check} dengan pola saat ini."
                print_success(s_msg)
        else:
            print_info(f"Direktori untuk pemeriksaan core dump tidak ada: {path_to_check}")

    if found_core_files_summary:
        analysis_notes.extend(found_core_files_summary)
    else:
        analysis_notes.append("Tidak ada file core dump yang ditemukan di lokasi pemeriksaan umum.")

    if analysis_notes:
        all_raw_outputs.append("\n--- Ringkasan Analisis Core Dump ---")
        all_raw_outputs.extend(analysis_notes)

    general_recommendation = "Rekomendasi Umum Core Dump: Nonaktifkan core dump di server produksi (ulimit -c 0, sysctl kernel.core_pattern=\"|/bin/false\") kecuali sangat dibutuhkan untuk debugging. Jika aktif, pastikan disimpan di lokasi aman dengan izin terbatas dan dibersihkan secara berkala."
    print_info(general_recommendation)
    all_raw_outputs.append(f"\n{general_recommendation}")

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        combined_raw_output = "Tidak ada output yang dihasilkan dari pemeriksaan core dump."
        if os.geteuid() != 0:
            combined_raw_output += f" {REQUIRED_ROOT_MESSAGE}"
        print_info(combined_raw_output)

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)

    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_core_dump_checks() 