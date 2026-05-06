"""Modul untuk deteksi serangan dari security tools secara single scan (Black-box).

Modul ini mendeteksi aktivitas dari tools seperti Subfinder, Katana, FFUF, Nuclei, 
Nmap, dan ParamSpider dengan menganalisis log files dan network connections.
Terintegrasi dengan sistem Telegram dan Ollama AI untuk analisis dan notifikasi.
"""
import os
import re
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_ai_suggestion
)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print_warning("psutil tidak terinstall. Network monitoring akan terbatas.")

@dataclass
class SecurityEvent:
    timestamp: str
    tool_name: str
    attack_type: str
    source_ip: str
    target: str
    severity: str
    details: Dict[str, Any]
    raw_log: str

class ToolSignatureDetector:
    def __init__(self):
        self.tool_signatures = {
            'subfinder': {'patterns': [r'subfinder', r'User-Agent.*subfinder', r'projectdiscovery\.io'], 'behavior': 'subdomain_enumeration'},
            'katana': {'patterns': [r'katana', r'User-Agent.*katana', r'web crawler'], 'behavior': 'web_crawling'},
            'ffuf': {'patterns': [r'ffuf', r'User-Agent.*ffuf', r'FUZZ'], 'behavior': 'directory_fuzzing'},
            'nuclei': {'patterns': [r'nuclei', r'User-Agent.*nuclei', r'projectdiscovery\.io'], 'behavior': 'vulnerability_scanning'},
            'nmap': {'patterns': [r'nmap', r'Nmap.*scan', r'SYN.*scan'], 'behavior': 'port_scanning'},
            'paramspider': {'patterns': [r'paramspider', r'User-Agent.*paramspider', r'parameter.*discovery'], 'behavior': 'parameter_discovery'}
        }
        self.severity_mapping = {
            'nmap': 'HIGH', 'nuclei': 'CRITICAL', 'ffuf': 'MEDIUM',
            'katana': 'LOW', 'subfinder': 'LOW', 'paramspider': 'MEDIUM'
        }

    def detect_tool(self, log_entry: str, target_tool: str = None) -> Optional[str]:
        log_lower = log_entry.lower()
        tools_by_priority = ['nuclei', 'ffuf', 'katana', 'paramspider', 'subfinder', 'nmap']
        
        if target_tool and target_tool.lower() in tools_by_priority:
            tools_by_priority = [target_tool.lower()]
            
        for tool_name in tools_by_priority:
            for pattern in self.tool_signatures[tool_name]['patterns']:
                if re.search(pattern, log_lower, re.IGNORECASE):
                    return tool_name
        return None

class SecurityMonitorManager:
    def __init__(self, target_tool: str = None):
        self.detector = ToolSignatureDetector()
        self.events = []
        self.log_paths = self._setup_log_paths()
        self.target_tool = target_tool

    def _setup_log_paths(self):
        log_paths = []
        potential_paths = [
            '/var/log/apache2/access.log', '/var/log/nginx/access.log',
            '/var/log/auth.log', '/var/log/syslog', '/var/log/httpd/access_log',
            'C:\\Windows\\System32\\LogFiles\\W3SVC1\\',
            'C:\\inetpub\\logs\\LogFiles\\W3SVC1\\',
            './logs/', './access.log', './error.log'
        ]
        for path in potential_paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    log_paths.append(path)
                elif os.path.isdir(path):
                    try:
                        for file in os.listdir(path):
                            if file.endswith(('.log', '.txt')):
                                log_paths.append(os.path.join(path, file))
                    except PermissionError:
                        continue
        return log_paths

    def start_monitoring_sync(self):
        self._detect_current_attacks()
        return self.events

    def _detect_current_attacks(self):
        print_info("Scanning for ongoing attacks...")
        if PSUTIL_AVAILABLE:
            self._scan_processes()
        self._check_recent_logs()

    def _scan_processes(self):
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        tool_detected = self.detector.detect_tool(cmdline, self.target_tool)
                        if tool_detected:
                            print_warning(f"Security tool detected: {tool_detected} (PID: {proc.info['pid']})")
                            event = SecurityEvent(
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                tool_name=tool_detected, attack_type="process",
                                source_ip="localhost", target="localhost", 
                                severity=self.detector.severity_mapping.get(tool_detected, "MEDIUM"),
                                details={"pid": proc.info['pid'], "cmdline": cmdline},
                                raw_log=cmdline
                            )
                            self.events.append(event)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print_warning(f"Error scanning processes: {e}")

    def _check_recent_logs(self):
        for log_path in self.log_paths:
            if not os.path.exists(log_path):
                continue
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    for line in recent_lines:
                        line = line.strip()
                        if line:
                            tool_detected = self.detector.detect_tool(line, self.target_tool)
                            if tool_detected:
                                print_warning(f"Attack pattern detected in {log_path}: {tool_detected}")
                                event = SecurityEvent(
                                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    tool_name=tool_detected, attack_type="log",
                                    source_ip="unknown", target="localhost",
                                    severity=self.detector.severity_mapping.get(tool_detected, "HIGH"),
                                    details={"log_file": log_path}, raw_log=line
                                )
                                self.events.append(event)
            except Exception as e:
                print_warning(f"Error reading log {log_path}: {e}")

def run_blackbox_checks(target_tool: str = None):
    test_name = f"Black-box Security Attack Detection{'' if not target_tool else f' ({target_tool.upper()})'}"
    print_header(test_name)
    try:
        manager = SecurityMonitorManager(target_tool)
        print_info(f"\n🔍 Starting Black-box One-time Scan Mode{'' if not target_tool else f' for {target_tool.upper()}'}...")
        events = manager.start_monitoring_sync()
        if events:
            print_success(f"\n✅ Scan selesai. Ditemukan {len(events)} security events:")
            for event in events:
                print_warning(f"- {event.tool_name} detected at {event.timestamp}")
            
            # AI Analysis and Telegram Alert for the findings
            findings_data = f"Ditemukan {len(events)} black-box security events:\n"
            for ev in events:
                findings_data += f"- {ev.tool_name} ({ev.attack_type}): {ev.raw_log[:100]}\n"
            
            ai_saran = get_ai_suggestion(test_name, findings_data)
            send_to_telegram(test_name, findings_data, ai_saran)
        else:
            print_success("\n✅ Scan selesai. Tidak ada serangan terdeteksi.")
    except Exception as e:
        error_msg = f"Error dalam blackbox detection: {e}"
        print_danger(error_msg)

if __name__ == "__main__":
    import sys
    tool = None
    if len(sys.argv) > 2 and sys.argv[1] == "--tool":
        tool = sys.argv[2]
    run_blackbox_checks(tool)
