import os # Untuk os.geteuid() agar lebih konsisten dengan root_checks.is_root()

# Modul utilitas dan checker dasar
import utils # Baru ditambahkan
import host_utils
import port_scanner
import ftp_checker
import ssh_checker
import web_checker

# Modul checker yang telah direfaktor/baru
import root_checks
import system_info_checker
import hardening_checker
import log_analyzer
import user_group_checker
import network_config_checker
import package_manager_checker
import cron_checker
import resource_limit_checker
import security_module_checker
import environment_checker
import ntp_checker
import inode_checker
import auditd_checker
import password_policy_checker
import integrity_checker # Menggantikan integrity_checker_stub
import shared_memory_checker
import kernel_module_checker
import motd_checker
import tmp_mount_checker
import usb_devices_checker
import core_dump_checker
import sticky_bit_checker
import compilers_presence_checker
import login_banner_checker
import securetty_checker
import tcp_wrappers_checker
import security_monitor

def is_root():
    return os.geteuid() == 0

def main():
    utils.print_header("MEMULAI PEMINDAIAN SERVER KOMPREHENSIF", char="=", color_code=utils.Colors.OKBLUE)

    utils.print_header("Pemeriksaan Informasi Sistem & Konfigurasi Umum", color_code=utils.Colors.OKGREEN)
    system_info_checker.run_system_info_checks()
    host_utils.run_host_utils_checks("localhost")
    network_config_checker.run_network_config_checks()
    package_manager_checker.run_package_manager_checks()
    cron_checker.run_cron_checks()
    resource_limit_checker.run_resource_limit_checks()
    environment_checker.run_environment_checks() 
    ntp_checker.run_ntp_checks()
    inode_checker.run_inode_checks()
    password_policy_checker.run_password_policy_checks()
    integrity_checker.run_integrity_checks()
    shared_memory_checker.run_shared_memory_checks()
    kernel_module_checker.run_kernel_module_checks()
    motd_checker.run_motd_checks()
    tmp_mount_checker.run_tmp_mount_checks()
    usb_devices_checker.run_usb_devices_checks()
    sticky_bit_checker.run_sticky_bit_checks()
    compilers_presence_checker.run_compilers_presence_checks()
    user_group_checker.run_user_group_checks()
    login_banner_checker.run_login_banner_checks()
    securetty_checker.run_securetty_checks()
    tcp_wrappers_checker.run_tcp_wrappers_checks()


    utils.print_header("Pemeriksaan Khusus Root & Keamanan Mendalam", color_code=utils.Colors.WARNING)
    if is_root():
        utils.print_info("Dijalankan sebagai root, melanjutkan dengan pengujian yang memerlukan privilese tinggi...")
        root_checks.run_root_checks()
        hardening_checker.run_hardening_checks()
        log_analyzer.run_log_analysis()
        security_module_checker.run_security_module_checks() 
        auditd_checker.run_auditd_checks() 
        core_dump_checker.run_core_dump_checks()
    else:
        utils.print_warning("\nTidak dijalankan sebagai root. Beberapa pengujian akan dilewati atau memberikan hasil terbatas.")
        utils.print_warning("    Pengujian yang sangat bergantung pada root (atau memberikan detail lebih):")
        utils.print_warning("    - Pengecekan Root Dasar (dari root_checks.py)")
        utils.print_warning("    - Pengecekan Hardening (hardening_checker.py)")
        utils.print_warning("    - Analisis Log (log_analyzer.py)")
        utils.print_warning("    - Detail Modul Keamanan (security_module_checker.py)")
        utils.print_warning("    - Aturan & Status Auditd (auditd_checker.py)")
        utils.print_warning("    - Detail Core Dump (core_dump_checker.py)")
        utils.print_info("    Untuk hasil paling komprehensif, jalankan skrip ini menggunakan sudo.")

    # Security monitoring untuk deteksi serangan real-time (untuk semua user)
    utils.print_header("Security Attack Detection & Monitoring", color_code=utils.Colors.WARNING)
    security_monitor.run_security_monitoring_checks()

    utils.print_header("Pemindaian Jaringan Lokal", color_code=utils.Colors.OKGREEN)
    target_host = "localhost"
    utils.print_info(f"Memulai pemindaian jaringan otomatis untuk {target_host}")
    
    host_utils.run_host_utils_checks(target_host)
    
    resolved_ip = host_utils.resolve_host(target_host)

    if resolved_ip:
        utils.print_info(f"Host {target_host} berhasil di-resolve ke {resolved_ip}")
        host_utils.ping_host(resolved_ip)
        
        common_ports = [
            20, 21, 22, 23, 25, 53, 80, 8080, 110, 135, 137, 138, 139, 143, 443, 8443, 445, 465, 587, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 5901, 6379, 27017, 27018
        ]
        
        port_scanner.run_port_scan_checks(resolved_ip, common_ports) # Memanggil fungsi utama port_scanner
        
        utils.print_info("Memeriksa layanan umum berdasarkan port standar jika terbuka...")
        # Cek FTP
        ftp_checker.run_ftp_checks(resolved_ip) # Akan cek port 21
        # Cek SSH
        ssh_checker.run_ssh_banner_checks(resolved_ip) # Akan cek port 22
        # Cek Web (HTTP/HTTPS pada port umum)
        web_checker.run_web_checks(resolved_ip) # Akan cek port 80, 443, 8080, 8443
        
    else:
        utils.print_warning(f"Tidak dapat melanjutkan pemindaian jaringan karena host {target_host} tidak dapat di-resolve.")

    utils.print_info(f"Pemindaian jaringan untuk {target_host} selesai.")
    
    utils.print_header("SEMUA PENGUJIAN SELESAI", char="=", color_code=utils.Colors.OKBLUE)
    
    # Tawarkan continuous monitoring
    utils.print_header("Opsi Real-time Security Monitoring", color_code=utils.Colors.WARNING)
    utils.print_info("Scan awal telah selesai. Anda dapat memulai monitoring real-time untuk mendeteksi serangan.")
    utils.print_info("Mode monitoring akan:")
    utils.print_info("• Memantau log files secara real-time")
    utils.print_info("• Mendeteksi aktivitas tools seperti Subfinder, Katana, FFUF, Nuclei, Nmap, ParamSpider")
    utils.print_info("• Melakukan analisis AI otomatis ketika serangan terdeteksi")
    utils.print_info("• Mengirim notifikasi Telegram langsung")
    
    try:
        choice = input("\nApakah ingin memulai continuous monitoring? (y/n): ").strip().lower()
        if choice in ['y', 'yes', 'ya']:
            utils.print_success("🚀 Memulai Continuous Security Monitoring...")
            monitor_manager = security_monitor.SecurityMonitorManager()
            monitor_manager.start_continuous_monitoring()
        else:
            utils.print_info("Monitoring tidak dimulai. Anda dapat menjalankannya nanti dengan:")
            utils.print_info("python security_monitor.py --continuous")
    except KeyboardInterrupt:
        utils.print_info("\nExiting...")

if __name__ == "__main__":
    main()