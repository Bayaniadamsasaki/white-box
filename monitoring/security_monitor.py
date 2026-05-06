"""Modul untuk monitoring dan deteksi serangan dari security tools secara real-time.

Modul ini mendeteksi aktivitas dari tools seperti Subfinder, Katana, FFUF, Nuclei, 
Nmap, dan ParamSpider dengan menganalisis log files dan network connections.
Terintegrasi dengan sistem Telegram dan Ollama AI untuk analisis dan notifikasi.
"""
import asyncio
import json
import re
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import subprocess
from pathlib import Path
import threading
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
    """Data class untuk menyimpan informasi event keamanan"""
    timestamp: str
    tool_name: str
    attack_type: str
    source_ip: str
    target: str
    severity: str
    details: Dict[str, Any]
    raw_log: str

class ToolSignatureDetector:
    """Kelas untuk mendeteksi signature dari berbagai security tools"""
    
    def __init__(self):
        self.tool_signatures = {
            'subfinder': {
                'patterns': [
                    r'subfinder',
                    r'User-Agent.*subfinder',
                    r'projectdiscovery\.io'
                ],
                'ports': [],
                'behavior': 'subdomain_enumeration'
            },
            'katana': {
                'patterns': [
                    r'katana',
                    r'User-Agent.*katana',
                    r'web crawler'
                ],
                'ports': [80, 443],
                'behavior': 'web_crawling'
            },
            'ffuf': {
                'patterns': [
                    r'ffuf',
                    r'User-Agent.*ffuf',
                    r'FUZZ'
                ],
                'ports': [80, 443],
                'behavior': 'directory_fuzzing'
            },
            'nuclei': {
                'patterns': [
                    r'nuclei',
                    r'User-Agent.*nuclei',
                    r'projectdiscovery\.io',
                    r'projectdiscovery'
                ],
                'ports': [80, 443],
                'behavior': 'vulnerability_scanning'
            },
            'nmap': {
                'patterns': [
                    r'nmap',
                    r'Nmap.*scan',
                    r'SYN.*scan'
                ],
                'ports': 'all',
                'behavior': 'port_scanning'
            },
            'paramspider': {
                'patterns': [
                    r'paramspider',
                    r'User-Agent.*paramspider',
                    r'parameter.*discovery'
                ],
                'ports': [80, 443],
                'behavior': 'parameter_discovery'
            }
        }
        
        self.severity_mapping = {
            'nmap': 'HIGH',
            'nuclei': 'CRITICAL',
            'ffuf': 'MEDIUM',
            'katana': 'LOW',
            'subfinder': 'LOW',
            'paramspider': 'MEDIUM'
        }
    
    def detect_tool(self, log_entry: str, connection_info: Dict = None) -> Optional[str]:
        """Mendeteksi tool berdasarkan log entry dan informasi koneksi"""
        log_lower = log_entry.lower()
        
        # Sort tools by specificity (lebih spesifik dulu)
        tools_by_priority = [
            'nuclei', 'ffuf', 'katana', 'paramspider', 'subfinder', 'nmap'
        ]
        
        for tool_name in tools_by_priority:
            if tool_name not in self.tool_signatures:
                continue
                
            signatures = self.tool_signatures[tool_name]
            
            # Check pattern signatures
            for pattern in signatures['patterns']:
                if re.search(pattern, log_lower, re.IGNORECASE):
                    return tool_name
            
            # Check port-based detection jika ada informasi koneksi
            if connection_info and 'dest_port' in connection_info:
                dest_port = connection_info['dest_port']
                if signatures['ports'] == 'all':
                    # Nmap bisa scan semua port
                    if self._is_port_scan_behavior(connection_info):
                        return tool_name
                elif dest_port in signatures.get('ports', []):
                    # Kombinasi port + behavior pattern
                    if any(re.search(p, log_lower, re.IGNORECASE) for p in signatures['patterns']):
                        return tool_name
        
        return None
    
    def _is_port_scan_behavior(self, connection_info: Dict) -> bool:
        """Mendeteksi behavior port scanning"""
        # Implementasi sederhana: banyak koneksi ke port berbeda dalam waktu singkat
        # Ini bisa diperluas dengan algoritma yang lebih sophisticated
        return connection_info.get('connection_count', 0) > 10

class LogMonitor:
    """Monitor log files untuk mendeteksi aktivitas security tools"""
    
    def __init__(self, log_paths: List[str]):
        self.log_paths = log_paths
        self.detector = ToolSignatureDetector()
        self.file_positions = {}
        self.connection_tracker = defaultdict(list)
        
    async def start_monitoring(self):
        """Mulai monitoring log files"""
        print_info("Memulai monitoring log files untuk deteksi serangan...")
        
        # Initialize file positions
        for log_path in self.log_paths:
            if Path(log_path).exists():
                with open(log_path, 'r') as f:
                    f.seek(0, 2)  # Go to end of file
                    self.file_positions[log_path] = f.tell()
        
        while True:
            try:
                await self._check_logs()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                print_danger(f"Error dalam log monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _check_logs(self):
        """Check for new log entries"""
        for log_path in self.log_paths:
            if not Path(log_path).exists():
                continue
                
            try:
                with open(log_path, 'r') as f:
                    # Go to last known position
                    f.seek(self.file_positions.get(log_path, 0))
                    new_lines = f.readlines()
                    self.file_positions[log_path] = f.tell()
                    
                    for line in new_lines:
                        await self._process_log_line(line.strip(), log_path)
                        
            except Exception as e:
                print_danger(f"Error membaca log file {log_path}: {e}")
    
    async def _process_log_line(self, line: str, source_file: str):
        """Process individual log line"""
        if not line:
            return
            
        # Extract connection info if available
        connection_info = self._extract_connection_info(line)
        
        # Detect tool
        detected_tool = self.detector.detect_tool(line, connection_info)
        
        if detected_tool:
            event = self._create_security_event(line, detected_tool, connection_info, source_file)
            await self._handle_security_event(event)
    
    def _extract_connection_info(self, log_line: str) -> Dict:
        """Extract connection information from log line"""
        info = {}
        
        # Extract IP addresses
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, log_line)
        if ips:
            info['source_ip'] = ips[0] if len(ips) > 0 else None
            info['dest_ip'] = ips[1] if len(ips) > 1 else None
        
        # Extract ports
        port_pattern = r':(\d{1,5})\b'
        ports = re.findall(port_pattern, log_line)
        if ports:
            info['dest_port'] = int(ports[0])
        
        # Extract HTTP method and path
        http_pattern = r'(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+([^\s]+)'
        http_match = re.search(http_pattern, log_line)
        if http_match:
            info['http_method'] = http_match.group(1)
            info['http_path'] = http_match.group(2)
        
        return info
    
    def _create_security_event(self, log_line: str, tool_name: str, 
                             connection_info: Dict, source_file: str) -> SecurityEvent:
        """Create SecurityEvent object"""
        return SecurityEvent(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            attack_type=self.detector.tool_signatures[tool_name]['behavior'],
            source_ip=connection_info.get('source_ip', 'unknown'),
            target=connection_info.get('dest_ip', 'localhost'),
            severity=self.detector.severity_mapping.get(tool_name, 'MEDIUM'),
            details=connection_info,
            raw_log=log_line
        )
    
    async def _handle_security_event(self, event: SecurityEvent):
        """Handle detected security event"""
        print_warning(f"SERANGAN TERDETEKSI: {event.tool_name} - {event.attack_type}")
        print_info(f"Source IP: {event.source_ip}, Target: {event.target}, Severity: {event.severity}")
        
        # Process dengan analyzer internal
        await self._process_security_event(event)
    
    async def _process_security_event(self, event: SecurityEvent):
        """Process security event dengan AI analysis dan kirim ke Telegram"""
        test_name = f"DETEKSI SERANGAN {event.tool_name.upper()}"
        
        # Format output untuk analisis
        event_details = f"""Tool: {event.tool_name}
Attack Type: {event.attack_type}
Source IP: {event.source_ip}
Target: {event.target}
Severity: {event.severity}
Timestamp: {event.timestamp}

Details: {json.dumps(event.details, indent=2)}

Raw Log: {event.raw_log}"""
        
        # Dapatkan saran dari AI
        ai_saran = get_ai_suggestion(test_name, event_details)
        
        # Kirim ke Telegram
        send_to_telegram(test_name, event_details, ai_saran)

class NetworkMonitor:
    """Monitor network connections untuk mendeteksi aktivitas suspicious"""
    
    def __init__(self):
        self.detector = ToolSignatureDetector()
        self.connection_history = defaultdict(list)
        self.suspicious_patterns = {
            'port_scan': {'threshold': 10, 'timeframe': 60},  # 10+ ports dalam 60 detik
            'rapid_requests': {'threshold': 50, 'timeframe': 30},  # 50+ request dalam 30 detik
        }
    
    async def start_monitoring(self):
        """Start network monitoring"""
        if not PSUTIL_AVAILABLE:
            print_warning("psutil tidak tersedia. Network monitoring dilewati.")
            return
            
        print_info("Memulai network monitoring untuk deteksi serangan...")
        
        while True:
            try:
                await self._check_connections()
                await asyncio.sleep(2)  # Check every 2 seconds
            except Exception as e:
                print_danger(f"Error dalam network monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _check_connections(self):
        """Check current network connections"""
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            connections = psutil.net_connections(kind='inet')
            current_time = time.time()
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    await self._analyze_connection(conn, current_time)
                    
        except Exception as e:
            print_danger(f"Error checking connections: {e}")
    
    async def _analyze_connection(self, connection, current_time):
        """Analyze individual connection"""
        remote_ip = connection.raddr.ip
        remote_port = connection.raddr.port
        local_port = connection.laddr.port
        
        # Track connection history
        conn_key = f"{remote_ip}:{local_port}"
        self.connection_history[conn_key].append({
            'timestamp': current_time,
            'remote_port': remote_port,
            'local_port': local_port
        })
        
        # Clean old entries (older than 5 minutes)
        cutoff_time = current_time - 300
        self.connection_history[conn_key] = [
            entry for entry in self.connection_history[conn_key]
            if entry['timestamp'] > cutoff_time
        ]
        
        # Check for suspicious patterns
        await self._check_suspicious_patterns(remote_ip, conn_key, current_time)
    
    async def _check_suspicious_patterns(self, remote_ip: str, conn_key: str, current_time: float):
        """Check for suspicious connection patterns"""
        history = self.connection_history[conn_key]
        
        # Check for port scanning
        recent_connections = [
            entry for entry in history
            if current_time - entry['timestamp'] <= self.suspicious_patterns['port_scan']['timeframe']
        ]
        
        unique_ports = len(set(entry['remote_port'] for entry in recent_connections))
        
        if unique_ports >= self.suspicious_patterns['port_scan']['threshold']:
            await self._handle_suspicious_activity('port_scan', remote_ip, {
                'unique_ports': unique_ports,
                'timeframe': self.suspicious_patterns['port_scan']['timeframe'],
                'connections': len(recent_connections)
            })
    
    async def _handle_suspicious_activity(self, activity_type: str, source_ip: str, details: Dict):
        """Handle detected suspicious activity"""
        print_warning(f"Aktivitas mencurigakan terdeteksi: {activity_type} dari {source_ip}")
        
        # Create security event
        event = SecurityEvent(
            timestamp=datetime.now().isoformat(),
            tool_name='unknown',
            attack_type=activity_type,
            source_ip=source_ip,
            target='localhost',
            severity='HIGH',
            details=details,
            raw_log=f"Network monitoring detected {activity_type} from {source_ip}"
        )
        
        # Send to internal analyzer
        await self._process_suspicious_event(event)
    
    async def _process_suspicious_event(self, event: SecurityEvent):
        """Process suspicious event dengan AI analysis dan kirim ke Telegram"""
        test_name = f"AKTIVITAS MENCURIGAKAN - {event.attack_type.upper()}"
        
        event_details = f"""Activity Type: {event.attack_type}
Source IP: {event.source_ip}
Target: {event.target}  
Severity: {event.severity}
Timestamp: {event.timestamp}

Network Details: {json.dumps(event.details, indent=2)}

Description: {event.raw_log}"""
        
        # Dapatkan saran dari AI
        ai_saran = get_ai_suggestion(test_name, event_details)
        
        # Kirim ke Telegram
        send_to_telegram(test_name, event_details, ai_saran)

class SecurityMonitorManager:
    """Manager untuk menjalankan monitoring security dari berbagai tools"""
    
    def __init__(self):
        self.detector = ToolSignatureDetector()
        self.events = []
        self.monitoring_active = False
        self.continuous_mode = False
        self.ai_alert_cooldown_sec = int(os.getenv("AI_ALERT_COOLDOWN_SEC", "300"))
        self._last_ai_alert = {}
        self._suppressed_counts = defaultdict(int)
        self._suppressed_last_detail = {}
        
        # Setup log monitoring paths
        self.log_paths = self._setup_log_paths()
        
        # Initialize network monitor jika psutil tersedia
        if PSUTIL_AVAILABLE:
            self.network_monitor = NetworkMonitor()
        else:
            self.network_monitor = None

    def _setup_log_paths(self):
        """Setup path untuk monitoring log files"""
        log_paths = []
        
        # Common log paths untuk deteksi serangan
        potential_paths = [
            '/var/log/apache2/access.log',
            '/var/log/nginx/access.log',
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/httpd/access_log',
            # Windows paths
            'C:\\Windows\\System32\\LogFiles\\W3SVC1\\',
            'C:\\inetpub\\logs\\LogFiles\\W3SVC1\\',
            # Local log files
            './logs/',
            './access.log',
            './error.log'
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    log_paths.append(path)
                elif os.path.isdir(path):
                    # Add all log files in directory
                    try:
                        for file in os.listdir(path):
                            if file.endswith(('.log', '.txt')):
                                log_paths.append(os.path.join(path, file))
                    except PermissionError:
                        continue
        
        return log_paths

    def start_continuous_monitoring(self):
        """Start continuous monitoring mode yang berjalan di background"""
        print_header("STARTING CONTINUOUS SECURITY MONITORING")
        print_info("Mode: Continuous Background Monitoring")
        print_info("Monitoring akan berjalan terus-menerus dan melakukan analisis otomatis ketika serangan terdeteksi")
        print_info("Tekan Ctrl+C untuk menghentikan monitoring\n")
        
        self.continuous_mode = True
        self.monitoring_active = True
        
        try:
            # Start log monitoring
            if self.log_paths:
                threading.Thread(target=self._continuous_log_monitoring, daemon=True).start()
                print_success("✓ Log monitoring started")
            else:
                print_warning("⚠ No log files found for monitoring")
            
            # Start network monitoring
            if self.network_monitor:
                threading.Thread(target=self._continuous_network_monitoring, daemon=True).start()
                print_success("✓ Network monitoring started")
            else:
                print_warning("⚠ Network monitoring tidak tersedia (psutil not installed)")
            
            print_success("🛡️  Continuous monitoring aktif - sistem siap mendeteksi serangan!")
            print_info("📊 Status akan ditampilkan ketika ada aktivitas mencurigakan")
            
            # Main monitoring loop
            while self.monitoring_active:
                try:
                    time.sleep(5)  # Check setiap 5 detik
                    
                except KeyboardInterrupt:
                    print_info("\n🛑 Menghentikan continuous monitoring...")
                    break
                    
        except Exception as e:
            print_danger(f"Error dalam continuous monitoring: {e}")
        finally:
            self.stop_monitoring()

    def _continuous_log_monitoring(self):
        """Monitoring log files secara continuous"""
        monitored_files = {}
        
        while self.monitoring_active:
            try:
                for log_path in self.log_paths:
                    if os.path.exists(log_path):
                        # Track file modification time
                        current_mtime = os.path.getmtime(log_path)
                        
                        if log_path not in monitored_files:
                            monitored_files[log_path] = {
                                'mtime': current_mtime,
                                'position': 0
                            }
                        
                        # Check if file was modified
                        if current_mtime > monitored_files[log_path]['mtime']:
                            self._process_new_log_entries(log_path, monitored_files[log_path])
                            monitored_files[log_path]['mtime'] = current_mtime
                
                time.sleep(2)  # Check log files setiap 2 detik
                
            except Exception as e:
                if self.monitoring_active:  # Only print if still monitoring
                    print_warning(f"Error dalam log monitoring: {e}")
                time.sleep(5)

    def _process_new_log_entries(self, log_path, file_info):
        """Process new entries dalam log file"""
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(file_info['position'])
                new_lines = f.readlines()
                file_info['position'] = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if line:
                        tool_detected = self.detector.detect_tool(line)
                        if tool_detected:
                            self._handle_attack_detection(tool_detected, line, 'log')
        except Exception as e:
            print_warning(f"Error reading log file {log_path}: {e}")

    def _continuous_network_monitoring(self):
        """Monitoring network connections secara continuous"""
        if not PSUTIL_AVAILABLE:
            return
            
        connection_history = {}
        
        while self.monitoring_active:
            try:
                connections = psutil.net_connections(kind='inet')
                current_time = time.time()
                
                for conn in connections:
                    if conn.raddr:  # Has remote address
                        remote_ip = conn.raddr.ip
                        remote_port = conn.raddr.port
                        
                        # Track connection patterns
                        key = f"{remote_ip}:{remote_port}"
                        if key not in connection_history:
                            connection_history[key] = []
                        
                        connection_history[key].append(current_time)
                        
                        # Clean old entries (keep only last 5 minutes)
                        connection_history[key] = [
                            t for t in connection_history[key] 
                            if current_time - t < 300
                        ]
                        
                        # Detect suspicious patterns
                        if len(connection_history[key]) > 10:  # Many connections in 5 min
                            self._handle_attack_detection(
                                'port_scan', 
                                f"Multiple connections from {remote_ip} to port {remote_port}",
                                'network'
                            )
                
                time.sleep(3)  # Check network setiap 3 detik
                
            except Exception as e:
                if self.monitoring_active:
                    print_warning(f"Error dalam network monitoring: {e}")
                time.sleep(5)

    def _handle_attack_detection(self, tool_name, details, source_type):
        """Handle ketika serangan terdeteksi - langsung analisis"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_key = f"{tool_name}:{source_type}"
        now_ts = time.time()
        last_ts = self._last_ai_alert.get(event_key, 0)
        
        print_danger(f"\n🚨 SERANGAN TERDETEKSI! [{timestamp}]")
        print_warning(f"Tool: {tool_name}")
        print_warning(f"Source: {source_type}")
        print_warning(f"Details: {details}")
        
        # Create security event
        event = SecurityEvent(
            timestamp=timestamp,
            tool_name=tool_name,
            attack_type=source_type,
            source_ip="unknown",  # Will be parsed from details if available
            target="localhost",
            severity="HIGH",
            details={"raw_data": details, "source": source_type},
            raw_log=details
        )
        
        self.events.append(event)

        # Rate limit AI analysis for repeated attacks of the same type
        if self.ai_alert_cooldown_sec > 0 and (now_ts - last_ts) < self.ai_alert_cooldown_sec:
            self._suppressed_counts[event_key] += 1
            self._suppressed_last_detail[event_key] = details
            print_info(
                f"AI analysis disuppressed untuk '{tool_name}' (cooldown {self.ai_alert_cooldown_sec}s)."
            )
            return

        self._last_ai_alert[event_key] = now_ts
        suppressed_count = self._suppressed_counts.pop(event_key, 0)
        if suppressed_count:
            event.details["suppressed_count"] = suppressed_count
            event.details["suppressed_window_sec"] = self.ai_alert_cooldown_sec
            last_detail = self._suppressed_last_detail.pop(event_key, None)
            if last_detail:
                event.details["last_suppressed_detail"] = last_detail
        
        # Langsung lakukan analisis
        self._immediate_analysis(event)

    def _immediate_analysis(self, event):
        """Lakukan analisis langsung ketika serangan terdeteksi"""
        try:
            print_info("🔍 Melakukan analisis otomatis...")
            
            # Prepare analysis data
            analysis_data = f"""SECURITY ALERT - IMMEDIATE ANALYSIS
Timestamp: {event.timestamp}
Tool Detected: {event.tool_name}
Attack Type: {event.attack_type}
Details: {event.details}

Raw Log: {event.raw_log}

System Status: Under Attack
Monitoring Mode: Continuous
"""
            
            # Get AI analysis
            print_info("🤖 Mendapatkan analisis AI...")
            ai_analysis = get_ai_suggestion(
                f"SECURITY ALERT - {event.tool_name.upper()} ATTACK DETECTED", 
                analysis_data
            )
            
            # Send immediate notification
            print_info("📱 Mengirim notifikasi darurat...")
            send_to_telegram(
                f"🚨 SERANGAN TERDETEKSI - {event.tool_name.upper()}", 
                analysis_data, 
                ai_analysis
            )
            
            print_success("✅ Analisis dan notifikasi selesai!")
            print_info("🛡️  Continuing monitoring...\n")
            
        except Exception as e:
            print_danger(f"Error dalam immediate analysis: {e}")

    def start_monitoring_sync(self):
        """Start monitoring dalam mode synchronous untuk one-time scan"""
        print_header("Security Attack Monitoring & Detection")
        
        # Detect current attacks
        self._detect_current_attacks()
        
        # Monitor for a short period
        print_info("Monitoring for attacks...")
        start_time = time.time()
        
        while time.time() - start_time < 30:  # Monitor for 30 seconds
            # Check for new log entries
            self._check_recent_logs()
            
            # Check network activity if available
            if self.network_monitor:
                self._check_network_activity()
            
            time.sleep(2)
        
        # Return results
        return self.events

    def _detect_current_attacks(self):
        """Detect serangan yang sedang berlangsung"""
        print_info("Scanning for ongoing attacks...")
        
        # Check running processes untuk security tools
        if PSUTIL_AVAILABLE:
            self._scan_processes()
        
        # Check recent log entries
        self._check_recent_logs()

    def _scan_processes(self):
        """Scan running processes untuk security tools"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        tool_detected = self.detector.detect_tool(cmdline)
                        if tool_detected:
                            print_warning(f"Security tool detected: {tool_detected} (PID: {proc.info['pid']})")
                            
                            event = SecurityEvent(
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                tool_name=tool_detected,
                                attack_type="process",
                                source_ip="localhost",
                                target="localhost", 
                                severity="MEDIUM",
                                details={"pid": proc.info['pid'], "cmdline": cmdline},
                                raw_log=cmdline
                            )
                            self.events.append(event)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print_warning(f"Error scanning processes: {e}")

    def _check_recent_logs(self):
        """Check recent log entries untuk attack patterns"""
        current_time = time.time()
        
        for log_path in self.log_paths:
            if not os.path.exists(log_path):
                continue
                
            try:
                # Only read recent lines (last 100 lines)
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        if line:
                            tool_detected = self.detector.detect_tool(line)
                            if tool_detected:
                                print_warning(f"Attack pattern detected in {log_path}: {tool_detected}")
                                
                                event = SecurityEvent(
                                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    tool_name=tool_detected,
                                    attack_type="log",
                                    source_ip="unknown",
                                    target="localhost",
                                    severity="HIGH",
                                    details={"log_file": log_path},
                                    raw_log=line
                                )
                                self.events.append(event)
                                
            except Exception as e:
                print_warning(f"Error reading log {log_path}: {e}")

    def _check_network_activity(self):
        """Check network activity untuk suspicious patterns"""
        try:
            connections = psutil.net_connections(kind='inet')
            suspicious_ports = [22, 23, 21, 80, 443, 3389, 5432, 3306]  # Common target ports
            
            for conn in connections:
                if conn.raddr and conn.raddr.port in suspicious_ports:
                    # This is a simple check - in real scenario, you'd want more sophisticated detection
                    if conn.status == 'ESTABLISHED':
                        print_info(f"Active connection to {conn.raddr.ip}:{conn.raddr.port}")
                        
        except Exception as e:
            print_warning(f"Error checking network activity: {e}")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print_info("Security monitoring dihentikan.")

def run_security_monitoring_checks():
    """Fungsi utama untuk menjalankan security monitoring checks - sesuai pola proyek"""
    test_name = "Security Tools Attack Detection & Monitoring"
    print_header(test_name)
    
    # Check if running on Unix-like system
    try:
        if hasattr(os, 'geteuid') and os.geteuid() != 0:
            print_warning("Security monitoring membutuhkan akses root untuk hasil optimal.")
    except AttributeError:
        print_info("Running pada sistem Windows - beberapa fitur akan disesuaikan.")
    
    try:
        monitor_manager = SecurityMonitorManager()
        
        # Test basic functionality
        print_info("Testing security monitoring components...")
        
        # Test signature detection
        detector = ToolSignatureDetector()
        test_logs = [
            "GET /admin HTTP/1.1 User-Agent: subfinder",
            "POST /login HTTP/1.1 User-Agent: ffuf/1.3.1",
            "SYN scan detected from 192.168.1.100"
        ]
        
        detected_tools = []
        for test_log in test_logs:
            tool = detector.detect_tool(test_log)
            if tool:
                detected_tools.append(f"Detected: {tool} in log: {test_log[:50]}...")
        
        raw_output = f"""Security Monitoring Test Results:

Available log paths: {len(monitor_manager.log_paths)}
{chr(10).join(monitor_manager.log_paths) if monitor_manager.log_paths else 'No log files found'}

Network monitoring: {'Available' if PSUTIL_AVAILABLE else 'Not available (psutil missing)'}

Tool detection test results:
{chr(10).join(detected_tools) if detected_tools else 'No tools detected in test logs'}

Security monitoring components: {'Ready' if (monitor_manager.log_paths or PSUTIL_AVAILABLE) else 'Limited functionality'}
"""
        
        print_success("Security monitoring components berhasil ditest")
        
        # Dapatkan saran dari AI
        ai_saran = get_ai_suggestion(test_name, raw_output)
        
        # Kirim ke Telegram
        send_to_telegram(test_name, raw_output, ai_saran)
        
        # Tawarkan untuk memulai monitoring
        print_info("\nSecurity monitoring test selesai.")
        print_info("Untuk memulai real-time monitoring, jalankan: python start_monitoring.py --continuous")
        
    except Exception as e:
        error_msg = f"Error dalam security monitoring: {e}"
        print_danger(error_msg)
        
        ai_saran = get_ai_suggestion(test_name, error_msg)
        send_to_telegram(test_name, error_msg, ai_saran)

if __name__ == "__main__":
    """Direct execution - start real-time monitoring"""
    import sys
    
    print_header("NULL Security Monitor - Real-time Attack Detection")
    print_info("Pilihan mode:")
    print_info("1. Continuous Monitoring (monitoring terus-menerus)")
    print_info("2. One-time Scan (scan sekali lalu selesai)")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        mode = "continuous"
    elif len(sys.argv) > 1 and sys.argv[1] == "--scan":
        mode = "scan"
    else:
        try:
            choice = input("\nPilih mode (1/2): ").strip()
            mode = "continuous" if choice == "1" else "scan"
        except KeyboardInterrupt:
            print_info("\nExiting...")
            sys.exit(0)
    
    try:
        manager = SecurityMonitorManager()
        
        if mode == "continuous":
            print_info("\n🚀 Starting Continuous Monitoring Mode...")
            manager.start_continuous_monitoring()
        else:
            print_info("\n🔍 Starting One-time Scan Mode...")
            events = manager.start_monitoring_sync()
            
            if events:
                print_success(f"\n✅ Scan selesai. Ditemukan {len(events)} security events:")
                for event in events:
                    print_warning(f"- {event.tool_name} detected at {event.timestamp}")
            else:
                print_success("\n✅ Scan selesai. Tidak ada serangan terdeteksi.")
                
    except KeyboardInterrupt:
        print_info("\nSecurity monitoring dihentikan oleh user.")
    except Exception as e:
        print_danger(f"Error dalam security monitoring: {e}")
        print_danger(f"Error dalam security monitoring: {e}")
