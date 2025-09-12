#!/usr/bin/env python3
"""
Attack Simulation Script - Untuk testing detection system
Script ini mensimulasikan log entries yang dihasilkan oleh various security tools
HANYA UNTUK TESTING - JANGAN DIGUNAKAN UNTUK SERANGAN REAL
"""

import time
import json
from datetime import datetime
from pathlib import Path
from security_monitor import ToolSignatureDetector, SecurityEvent, LogMonitor
from utils import print_info, print_success, print_warning, print_danger, print_header

class AttackSimulator:
    """Simulate attacks untuk testing detection system"""
    
    def __init__(self, log_file_path=None):
        if log_file_path is None:
            # Use current directory for Windows compatibility
            log_file_path = Path("test_security.log").absolute()
        else:
            log_file_path = Path(log_file_path)
            
        self.log_file = log_file_path
        self.detector = ToolSignatureDetector()
        
        # Ensure log file exists
        self.log_file.touch(exist_ok=True)
        
    def simulate_subfinder_attack(self):
        """Simulate Subfinder subdomain enumeration"""
        print_info("Simulating Subfinder attack...")
        
        logs = [
            '192.168.1.100 - - [13/Aug/2025:10:30:45 +0000] "GET / HTTP/1.1" 200 1234 "-" "subfinder v2.5.5"',
            '192.168.1.100 - - [13/Aug/2025:10:30:46 +0000] "GET /api HTTP/1.1" 200 1234 "-" "subfinder"',
            '192.168.1.100 - - [13/Aug/2025:10:30:47 +0000] "GET /admin HTTP/1.1" 403 1234 "-" "subfinder - projectdiscovery.io"'
        ]
        
        for log in logs:
            self._write_log(log)
            time.sleep(0.5)
    
    def simulate_ffuf_attack(self):
        """Simulate FFUF directory fuzzing"""
        print_info("Simulating FFUF attack...")
        
        directories = ['admin', 'login', 'dashboard', 'config', 'backup', 'api', 'test']
        
        for directory in directories:
            log = f'192.168.1.100 - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S")} +0000] "GET /{directory} HTTP/1.1" 404 1234 "-" "ffuf/1.3.1"'
            self._write_log(log)
            time.sleep(0.2)
    
    def simulate_nuclei_attack(self):
        """Simulate Nuclei vulnerability scanning"""
        print_info("Simulating Nuclei attack...")
        
        vulnerable_paths = ['/.env', '/config.php', '/.git/config', '/admin/config.php', '/wp-config.php']
        
        for path in vulnerable_paths:
            log = f'192.168.1.100 - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S")} +0000] "GET {path} HTTP/1.1" 404 1234 "-" "nuclei v2.7.7"'
            self._write_log(log)
            time.sleep(0.3)
    
    def simulate_katana_attack(self):
        """Simulate Katana web crawling"""
        print_info("Simulating Katana attack...")
        
        paths = ['/robots.txt', '/sitemap.xml', '/index.html', '/about.html', '/contact.html']
        
        for path in paths:
            log = f'192.168.1.100 - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S")} +0000] "GET {path} HTTP/1.1" 200 1234 "-" "katana v1.0.3"'
            self._write_log(log)
            time.sleep(0.4)
    
    def simulate_paramspider_attack(self):
        """Simulate ParamSpider parameter discovery"""
        print_info("Simulating ParamSpider attack...")
        
        params = ['?id=1', '?user=admin', '?page=home', '?category=test', '?search=query']
        
        for param in params:
            log = f'192.168.1.100 - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S")} +0000] "GET /{param} HTTP/1.1" 200 1234 "-" "paramspider"'
            self._write_log(log)
            time.sleep(0.3)
    
    def simulate_nmap_attack(self):
        """Simulate Nmap port scanning (system log style)"""
        print_info("Simulating Nmap attack...")
        
        nmap_logs = [
            f'kernel: [{int(time.time())}] iptables: Nmap scan blocked: IN=eth0 OUT= SRC=192.168.1.100 DST=192.168.1.10',
            f'kernel: [{int(time.time())}] SYN scan detected from 192.168.1.100 targeting ports 22,80,443',
            f'sshd[1234]: Connection from 192.168.1.100 port scanning detected'
        ]
        
        for log in nmap_logs:
            self._write_log(log)
            time.sleep(0.5)
    
    def _write_log(self, log_entry):
        """Write log entry to file"""
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
        print_success(f"Log written: {log_entry[:50]}...")
    
    def run_full_simulation(self):
        """Run simulation of all attack types"""
        print_header("MEMULAI SIMULASI SERANGAN UNTUK TESTING")
        print_warning("Ini adalah simulasi untuk testing detection system")
        print_info(f"Log file: {self.log_file}")
        
        try:
            # Clear previous logs
            with open(self.log_file, 'w') as f:
                f.write(f"# Attack simulation started at {datetime.now()}\n")
            
            # Simulate different attacks
            self.simulate_subfinder_attack()
            time.sleep(2)
            
            self.simulate_ffuf_attack()  
            time.sleep(2)
            
            self.simulate_nuclei_attack()
            time.sleep(2)
            
            self.simulate_katana_attack()
            time.sleep(2)
            
            self.simulate_paramspider_attack()
            time.sleep(2)
            
            self.simulate_nmap_attack()
            
            print_header("SIMULASI SELESAI")
            print_success(f"Log file tersedia di: {self.log_file}")
            print_info("Sekarang jalankan security_monitor.py untuk mendeteksi serangan")
            
        except Exception as e:
            print_danger(f"Error dalam simulasi: {e}")

def test_detection_on_simulated_logs():
    """Test detection system pada simulated logs"""
    print_header("TESTING DETECTION PADA SIMULATED LOGS")
    
    log_file = Path("test_security.log").absolute()
    if not log_file.exists():
        print_warning("Simulated log file tidak ditemukan. Jalankan simulasi terlebih dahulu.")
        return 0
    
    detector = ToolSignatureDetector()
    detected_attacks = []
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print_info(f"Analyzing {len(lines)} log entries...")
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        detected_tool = detector.detect_tool(line)
        if detected_tool:
            detected_attacks.append({
                'line': i,
                'tool': detected_tool,
                'log': line[:80] + '...' if len(line) > 80 else line
            })
    
    print_header("HASIL DETEKSI")
    
    if detected_attacks:
        print_success(f"Berhasil mendeteksi {len(detected_attacks)} serangan:")
        
        for attack in detected_attacks:
            print_info(f"Line {attack['line']}: {attack['tool'].upper()}")
            print_info(f"  Log: {attack['log']}")
            severity = detector.severity_mapping.get(attack['tool'], 'MEDIUM')
            print_info(f"  Severity: {severity}")
            print_info("")
    else:
        print_warning("Tidak ada serangan yang terdeteksi")
    
    return len(detected_attacks)

if __name__ == "__main__":
    print_header("ATTACK SIMULATION & DETECTION TESTING")
    
    try:
        simulator = AttackSimulator()
        
        choice = input("\nPilihan:\n1. Run simulasi serangan\n2. Test detection pada log yang ada\n3. Keduanya\nPilih (1-3): ")
        
        if choice in ['1', '3']:
            simulator.run_full_simulation()
            print_info("\nMenunggu 3 detik sebelum testing detection...")
            time.sleep(3)
        
        if choice in ['2', '3']:
            detected_count = test_detection_on_simulated_logs()
            
            if detected_count > 0:
                print_success(f"\n✓ Detection system berhasil mendeteksi {detected_count} serangan")
            else:
                print_warning("\n⚠ Detection system tidak mendeteksi serangan apapun")
        
        print_header("TESTING SELESAI")
        print_info("Untuk real-time monitoring, jalankan: python security_monitor.py")
        
    except KeyboardInterrupt:
        print_info("\nTesting dihentikan oleh user")
    except Exception as e:
        print_danger(f"Error: {e}")
