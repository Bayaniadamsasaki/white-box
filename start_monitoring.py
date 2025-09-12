#!/usr/bin/env python3
"""
NULL Security Monitor - Continuous Attack Detection
Script untuk memulai monitoring real-time serangan security tools.

Usage:
    python start_monitoring.py          # Interactive mode
    python start_monitoring.py --continuous  # Direct continuous mode
    python start_monitoring.py --scan        # One-time scan mode
"""

import sys
import os
from security_monitor import SecurityMonitorManager
from utils import print_header, print_info, print_success, print_warning, print_danger

def main():
    print_header("NULL Security Monitor - Real-time Attack Detection")
    print_info("Sistem monitoring untuk mendeteksi serangan dari blackbox tools:")
    print_info("• Subfinder (subdomain enumeration)")
    print_info("• Katana (web crawling)")  
    print_info("• FFUF (web fuzzing)")
    print_info("• Nuclei (vulnerability scanning)")
    print_info("• Nmap (port scanning)")
    print_info("• ParamSpider (parameter discovery)")
    print_info("")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            mode = "continuous"
        elif sys.argv[1] == "--scan":
            mode = "scan"
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_usage()
            return
        else:
            print_warning(f"Unknown argument: {sys.argv[1]}")
            print_usage()
            return
    else:
        # Interactive mode
        print_info("Pilihan mode monitoring:")
        print_info("1. Continuous Monitoring - monitoring terus-menerus di background")
        print_info("2. One-time Scan - scan sekali untuk deteksi serangan saat ini")
        print_info("3. Exit")
        
        try:
            choice = input("\nPilih mode (1/2/3): ").strip()
            if choice == "1":
                mode = "continuous"
            elif choice == "2":
                mode = "scan"
            elif choice == "3":
                print_info("Exiting...")
                return
            else:
                print_warning("Pilihan tidak valid.")
                return
        except KeyboardInterrupt:
            print_info("\nExiting...")
            return
    
    try:
        manager = SecurityMonitorManager()
        
        if mode == "continuous":
            print_success("\n🚀 Starting Continuous Monitoring Mode...")
            print_info("Sistem akan:")
            print_info("• Monitor log files secara real-time")
            print_info("• Deteksi network activity mencurigakan")
            print_info("• Analisis AI otomatis ketika serangan terdeteksi")
            print_info("• Kirim notifikasi Telegram langsung")
            print_info("\nTekan Ctrl+C untuk menghentikan monitoring\n")
            
            manager.start_continuous_monitoring()
            
        elif mode == "scan":
            print_success("\n🔍 Starting One-time Scan Mode...")
            print_info("Scanning untuk serangan yang sedang berlangsung...")
            
            events = manager.start_monitoring_sync()
            
            if events:
                print_danger(f"\n⚠️  SECURITY EVENTS DETECTED!")
                print_warning(f"Ditemukan {len(events)} security events:")
                for i, event in enumerate(events, 1):
                    print_warning(f"{i}. {event.tool_name} - {event.attack_type} at {event.timestamp}")
                    print_info(f"   Details: {event.raw_log[:100]}...")
                print_info("\nUntuk monitoring real-time, gunakan mode continuous.")
            else:
                print_success("\n✅ Scan selesai. Tidak ada serangan terdeteksi saat ini.")
                print_info("Sistem aman untuk saat ini. Untuk monitoring berkelanjutan, gunakan mode continuous.")
                
    except KeyboardInterrupt:
        print_info("\nSecurity monitoring dihentikan oleh user.")
    except Exception as e:
        print_danger(f"Error dalam security monitoring: {e}")
        print_info("Pastikan:")
        print_info("• File konfigurasi .env sudah benar")
        print_info("• Koneksi internet tersedia (untuk Telegram & Gemini)")
        print_info("• Dependencies sudah terinstall (pip install -r requirements.txt)")

def print_usage():
    print_info("\nUsage:")
    print_info("  python start_monitoring.py                 # Interactive mode")
    print_info("  python start_monitoring.py --continuous    # Continuous monitoring")
    print_info("  python start_monitoring.py --scan          # One-time scan")
    print_info("  python start_monitoring.py --help          # Show this help")

if __name__ == "__main__":
    main()
