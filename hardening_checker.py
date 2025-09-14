"""Modul untuk memeriksa berbagai aspek pengerasan (hardening) sistem.

Ini mencakup pemeriksaan status Fail2ban, konfigurasi SSHD, parameter kernel,
layanan yang diaktifkan, file world-writable di direktori kritis, opsi fstab,
dan akun dengan password kosong.
"""
import os
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion,
    capture_command_output, capture_read_file_content
)

REQUIRED_ROOT_MESSAGE = "Peringatan: Banyak pemeriksaan dalam modul ini memerlukan hak akses root."

SSHD_CONFIG_PATH = "/etc/ssh/sshd_config"
FSTAB_PATH = "/etc/fstab"
SHADOW_PATH = "/etc/shadow"

def run_hardening_checks():
    test_name = "Pemeriksaan Pengerasan (Hardening) Sistem"
    print_header(test_name)

    if os.geteuid() != 0:
        print_warning(REQUIRED_ROOT_MESSAGE)

    all_raw_outputs = []

    tests_definitions = [
        # Fail2Ban
        {"desc": "Status Layanan Fail2ban (systemctl)", "type": "cmd", "args": ["sudo", "systemctl", "is-active", "fail2ban"]},
        {"desc": "Fail2ban Client Ping", "type": "cmd", "args": ["sudo", "fail2ban-client", "ping"]},
        
        {"desc": f"Analisis Konfigurasi SSHD ({SSHD_CONFIG_PATH})", "type": "custom", "func_name": "analyze_sshd_config"},

        # Kernel Parameters
        {"desc": "Kernel: TCP SYN Cookies (net.ipv4.tcp_syncookies)", "type": "cmd", "args": ["sudo", "sysctl", "net.ipv4.tcp_syncookies"]},
        {"desc": "Kernel: IP Forwarding (net.ipv4.ip_forward)", "type": "cmd", "args": ["sudo", "sysctl", "net.ipv4.ip_forward"]},
        {"desc": "Kernel: ICMP Redirect Acceptance (net.ipv4.conf.all.accept_redirects)", "type": "cmd", "args": ["sudo", "sysctl", "net.ipv4.conf.all.accept_redirects"]},
        {"desc": "Kernel: ICMP Redirect Acceptance (net.ipv4.conf.default.accept_redirects)", "type": "cmd", "args": ["sudo", "sysctl", "net.ipv4.conf.default.accept_redirects"]},


        # Enabled Services
        {"desc": "Layanan yang Diaktifkan saat Boot (systemctl)", "type": "cmd", "args": ["systemctl", "list-unit-files", "--state=enabled", "--no-pager"]},

        # World-writable files
        {"desc": "File World-Writable di /etc", "type": "cmd", "args": ["sudo", "find", "/etc/", "-xdev", "-type", "f", "-perm", "-0002", "-print0", "|", "xargs", "-0", "ls", "-ld"]},
        {"desc": "File World-Writable di /bin /sbin /usr/bin /usr/sbin", "type": "cmd", "args": ["sudo", "find", "/bin", "/sbin", "/usr/bin", "/usr/sbin", "-xdev", "-type", "f", "-perm", "-0002", "-print0", "|", "xargs", "-0", "ls", "-ld"]},

        # /etc/fstab options
        {"desc": f"Analisis Opsi Mount di {FSTAB_PATH}", "type": "custom", "func_name": "analyze_fstab"},

        # Akun dengan password kosong
        {"desc": f"Pemeriksaan Akun dengan Password Kosong ({SHADOW_PATH})", "type": "custom", "func_name": "check_empty_passwords"}
    ]

    def analyze_sshd_config_internal():
        captured_lines = []
        desc = f"Analisis Konfigurasi SSHD ({SSHD_CONFIG_PATH})"
        captured_lines.append(f"Memulai: {desc}")
        print_info(f"Memulai: {desc}")

        content = capture_read_file_content(SSHD_CONFIG_PATH, "Baca SSHD Config")
        captured_lines.append(content)

        raw_sshd_content = ""
        if os.path.exists(SSHD_CONFIG_PATH):
            try:
                with open(SSHD_CONFIG_PATH, "r") as f_sshd:
                    raw_sshd_content = f_sshd.read()
            except Exception as e:
                msg = f"Gagal membaca konten mentah {SSHD_CONFIG_PATH} untuk analisis: {e}"
                print_danger(msg)
                captured_lines.append(msg)
        
        if raw_sshd_content:
            recommendations = []
            # PermitRootLogin
            if "PermitRootLogin yes" in raw_sshd_content and not "PermitRootLogin prohibit-password" in raw_sshd_content and not "PermitRootLogin without-password" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'PermitRootLogin prohibit-password' atau 'no' jika login root via SSH tidak diperlukan.")
            # PasswordAuthentication
            if "PasswordAuthentication yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'PasswordAuthentication no' dan menggunakan key-based authentication.")
            # X11Forwarding
            if "X11Forwarding yes" in raw_sshd_content:
                recommendations.append("SSHD: Nonaktifkan 'X11Forwarding no' jika tidak diperlukan.")
            # Cek parameter lain: ChallengeResponseAuthentication, UsePAM, etc.
            if "ChallengeResponseAuthentication yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'ChallengeResponseAuthentication no'.")
            if "UsePAM yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'UsePAM no'.")
            if "KerberosAuthentication yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'KerberosAuthentication no'.")
            if "KerberosOrLocalPasswd yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'KerberosOrLocalPasswd no'.")
            if "KerberosTicketCleanup yes" in raw_sshd_content:
                recommendations.append("SSHD: Pertimbangkan untuk mengatur 'KerberosTicketCleanup no'.")
                
            if not recommendations:
                msg = "SSHD: Beberapa praktik terbaik umum tampaknya sudah diterapkan atau tidak terdeteksi (analisis sederhana)."
                print_success(msg)
                captured_lines.append(msg)
            else:
                for rec in recommendations:
                    print_warning(rec)
                    captured_lines.append(f"Peringatan: {rec}")
        else:
            msg = f"Konten mentah {SSHD_CONFIG_PATH} tidak dapat dibaca untuk analisis mendalam."
            print_warning(msg)
            captured_lines.append(msg)
        return "\n".join(captured_lines)

    def analyze_fstab_internal():
        captured_lines = []
        desc = f"Analisis Opsi Mount di {FSTAB_PATH}"
        captured_lines.append(f"Memulai: {desc}")
        print_info(f"Memulai: {desc}")

        content = capture_read_file_content(FSTAB_PATH, "Baca fstab")
        captured_lines.append(content)
        raw_fstab_content = ""
        if os.path.exists(FSTAB_PATH):
            try:
                with open(FSTAB_PATH, "r") as f_fstab:
                    raw_fstab_content = f_fstab.read()
            except Exception as e:
                msg = f"Gagal membaca konten mentah {FSTAB_PATH} untuk analisis: {e}"
                print_danger(msg)
                captured_lines.append(msg)

        if raw_fstab_content:
            recommendations = []
            mount_points_to_check = {
                "/tmp": ["noexec", "nosuid", "nodev"],
                "/home": ["nodev"], # nodev adalah yang paling umum direkomendasikan untuk /home
                "/dev/shm": ["noexec", "nosuid", "nodev"] # Jika ada
            }
            for line in raw_fstab_content.splitlines():
                if line.strip().startswith("#") or not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    mount_point = parts[1]
                    options = parts[3].split(",") if len(parts) >= 4 else []
                    if mount_point in mount_points_to_check:
                        missing_opts = [opt for opt in mount_points_to_check[mount_point] if opt not in options]
                        if missing_opts:
                            recommendations.append(f"FSTAB: Untuk '{mount_point}', pertimbangkan menambahkan opsi: {', '.join(missing_opts)}.")
            if not recommendations:
                msg = "FSTAB: Opsi mount umum yang direkomendasikan untuk /tmp, /home, /dev/shm tampaknya ada atau partisi tidak terdefinisi (analisis sederhana)."
                print_success(msg)
                captured_lines.append(msg)
            else:
                for rec in recommendations:
                    print_warning(rec)
                    captured_lines.append(f"Peringatan: {rec}")
        else:
            msg = f"Konten mentah {FSTAB_PATH} tidak dapat dibaca untuk analisis mendalam."
            print_warning(msg)
            captured_lines.append(msg)
        return "\n".join(captured_lines)

    def check_empty_passwords_internal():
        captured_lines = []
        desc = f"Pemeriksaan Akun dengan Password Kosong ({SHADOW_PATH})"
        captured_lines.append(f"Memulai: {desc}")
        print_info(f"Memulai: {desc}")

        if os.geteuid() != 0:
            msg = f"Peringatan: Membaca {SHADOW_PATH} memerlukan hak root. Pengecekan dilewati."
            print_warning(msg)
            captured_lines.append(msg)
            return "\n".join(captured_lines)

        content = capture_read_file_content(SHADOW_PATH, "Baca Shadow File")
        captured_lines.append(content)
        raw_shadow_content = ""
        if os.path.exists(SHADOW_PATH):
            try:
                with open(SHADOW_PATH, "r") as f_shadow:
                    raw_shadow_content = f_shadow.read()
            except Exception as e:
                msg = f"Gagal membaca konten mentah {SHADOW_PATH} untuk analisis: {e}"
                print_danger(msg)
                captured_lines.append(msg)
        
        empty_password_accounts = []
        if raw_shadow_content:
            for line in raw_shadow_content.splitlines():
                fields = line.split(":")
                if len(fields) > 1:
                    username = fields[0]
                    password_hash = fields[1]
                    
                    if not password_hash or password_hash in ["", "*"] :
                        if not password_hash: 
                            empty_password_accounts.append(username)
            
            if empty_password_accounts:
                msg = f"Ditemukan akun yang mungkin memiliki password kosong: {', '.join(empty_password_accounts)}. Ini adalah risiko keamanan serius."
                print_danger(msg)
                captured_lines.append(msg)
                for acc in empty_password_accounts:
                    print_danger(f"   - Akun: {acc}")
            else:
                msg = f"Tidak ada akun dengan field password kosong terdeteksi di {SHADOW_PATH} (berdasarkan analisis sederhana)."
                print_success(msg)
                captured_lines.append(msg)
        else:
            msg = f"Konten mentah {SHADOW_PATH} tidak dapat dibaca untuk analisis password kosong."
            print_warning(msg)
            captured_lines.append(msg)
        return "\n".join(captured_lines)

    custom_dispatch = {
        "analyze_sshd_config": analyze_sshd_config_internal,
        "analyze_fstab": analyze_fstab_internal,
        "check_empty_passwords": check_empty_passwords_internal
    }

    for test_info in tests_definitions:
        description = test_info["desc"]
        test_type = test_info["type"]
        
        output_result = ""
        if test_type == "cmd":
            arguments = test_info["args"]
            output_result = capture_command_output(arguments, description)
        elif test_type == "file":
            file_path = test_info["args"]
            output_result = capture_read_file_content(file_path, description)
        elif test_type == "custom":
            func_name = test_info["func_name"]
            if func_name in custom_dispatch:
                output_result = custom_dispatch[func_name]()
            else:
                output_result = f"Fungsi kustom '{func_name}' tidak ditemukan untuk tes '{description}'."
                print_danger(output_result)
        
        if output_result and output_result.strip():
            all_raw_outputs.append(output_result)
            all_raw_outputs.append("\n---")

    if all_raw_outputs and all_raw_outputs[-1] == "\n---":
        all_raw_outputs.pop()
        
    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        msg = "Tidak ada output yang dihasilkan dari pemeriksaan hardening."
        if os.geteuid() != 0:
            msg = f"{REQUIRED_ROOT_MESSAGE}\n{msg} Kemungkinan karena kurangnya hak akses root."
        print_warning(msg)
        combined_raw_output = msg

    ai_saran = get_ai_suggestion(test_name, combined_raw_output)
    print_info(f"Saran dari AI: {ai_saran}")
    
    send_to_telegram(test_name, combined_raw_output, ai_saran)

if __name__ == '__main__':
    run_hardening_checks() 