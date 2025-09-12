#!/usr/bin/env python3
"""
NULL Security System - Quick Launcher
Simple banner dengan opsi white box dan blackbox
"""

import os
import sys
from utils import Colors

def show_banner():
    """Display simple banner dengan opsi"""
    banner = f"""{Colors.OKBLUE}{Colors.BOLD}
 ███╗   ██╗██╗   ██╗██╗     ██╗          ███████╗███████╗ ██████╗
 ████╗  ██║██║   ██║██║     ██║          ██╔════╝██╔════╝██╔════╝
 ██╔██╗ ██║██║   ██║██║     ██║          ███████╗█████╗  ██║     
 ██║╚██╗██║██║   ██║██║     ██║          ╚════██║██╔══╝  ██║     
 ██║ ╚████║╚██████╔╝███████╗███████╗     ███████║███████╗╚██████╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝     ╚══════╝╚══════╝ ╚═════╝{Colors.ENDC}

{Colors.HEADER}🛡️  INTEGRATED CYBERSECURITY SCANNER WITH AI ANALYSIS  🛡️{Colors.ENDC}
{Colors.OKGREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}
"""
    print(banner)

def show_options():
    """Display scanning options"""
    print(f"""
{Colors.BOLD}🎯 PILIH MODE SCANNING:{Colors.ENDC}

{Colors.OKGREEN}┌─ 🔍 WHITE-BOX SECURITY SCANNING ─────────────────────────────────────┐{Colors.ENDC}
{Colors.OKGREEN}│  Internal System Security Assessment & Vulnerability Analysis         │{Colors.ENDC}
{Colors.OKGREEN}└───────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[1]{Colors.ENDC} 🔍 Full Security Scan       - Complete system audit (30+ checks)
  {Colors.BOLD}[2]{Colors.ENDC} ⚡ Quick Security Check     - Essential security validation
  {Colors.BOLD}[3]{Colors.ENDC} 🔧 Individual Module Check - Specific security component

{Colors.WARNING}┌─ 🚨 BLACK-BOX ATTACK DETECTION ──────────────────────────────────────┐{Colors.ENDC}
{Colors.WARNING}│  Real-time External Attack Monitoring & Intrusion Detection          │{Colors.ENDC}
{Colors.WARNING}└───────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[4]{Colors.ENDC} 🚨 Real-time Monitor        - 24/7 attack detection (continuous)
  {Colors.BOLD}[5]{Colors.ENDC} 🔍 Single Attack Scan       - One-time attack detection scan
  {Colors.BOLD}[6]{Colors.ENDC} ⏱️  Custom Interval Monitor  - Periodic monitoring (custom time)

{Colors.OKBLUE}┌─ ⚙️ CONFIGURATION & HELP ────────────────────────────────────────────┐{Colors.ENDC}
{Colors.OKBLUE}│  System Configuration, Testing & Documentation                        │{Colors.ENDC}
{Colors.OKBLUE}└───────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[7]{Colors.ENDC} 🎮 Interactive Menu         - Full featured CLI interface
  {Colors.BOLD}[8]{Colors.ENDC} ⚙️  Setup & Configuration    - Configure API keys & settings
  {Colors.BOLD}[9]{Colors.ENDC} 📋 Commands Guide           - Show all available commands

  {Colors.BOLD}[0]{Colors.ENDC} 🚪 Exit                     - Exit program
""")

def main():
    """Main launcher function"""
    try:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        show_banner()
        show_options()
        
        choice = input(f"\n{Colors.BOLD}Pilih opsi [0-9]: {Colors.ENDC}").strip()
        
        print(f"\n{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
        
        if choice == "1":
            print(f"{Colors.OKGREEN}🔍 Starting White-box Full Security Scan...{Colors.ENDC}")
            os.system("python main_scanner.py")
            
        elif choice == "2":
            print(f"{Colors.OKGREEN}⚡ Starting White-box Quick Security Check...{Colors.ENDC}")
            print("Quick checks available:")
            print("  [a] SSH + Users      [b] Network + Ports     [c] System + Hardening")
            sub = input("Choose [a/b/c] or Enter for all: ").strip().lower()
            
            if sub == "a":
                os.system("python ssh_checker.py && python user_group_checker.py")
            elif sub == "b":
                os.system("python network_config_checker.py && python port_scanner.py")
            elif sub == "c":
                os.system("python system_info_checker.py && python hardening_checker.py")
            else:
                os.system("python ssh_checker.py && python user_group_checker.py && python system_info_checker.py")
                
        elif choice == "3":
            print(f"{Colors.OKGREEN}🔧 Individual Module Selection...{Colors.ENDC}")
            modules = [
                ("ssh_checker.py", "SSH Security"),
                ("user_group_checker.py", "User & Groups"),
                ("hardening_checker.py", "System Hardening"),
                ("web_checker.py", "Web Services"),
                ("port_scanner.py", "Port Scanning"),
                ("network_config_checker.py", "Network Config")
            ]
            
            print("Available modules:")
            for i, (script, desc) in enumerate(modules, 1):
                print(f"  [{i}] {desc}")
            
            mod_choice = input("Select module [1-6]: ").strip()
            try:
                idx = int(mod_choice) - 1
                if 0 <= idx < len(modules):
                    script, desc = modules[idx]
                    print(f"Running {desc}...")
                    os.system(f"python {script}")
                else:
                    print("Invalid module choice")
            except:
                print("Invalid input")
                
        elif choice == "4":
            print(f"{Colors.WARNING}🚨 Starting Black-box Real-time Attack Monitor...{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  Press Ctrl+C to stop monitoring{Colors.ENDC}")
            os.system("python start_monitoring.py --continuous")
            
        elif choice == "5":
            print(f"{Colors.WARNING}🔍 Starting Black-box Single Attack Scan...{Colors.ENDC}")
            os.system("python start_monitoring.py --single")
            
        elif choice == "6":
            print(f"{Colors.WARNING}⏱️ Starting Black-box Custom Interval Monitor...{Colors.ENDC}")
            try:
                interval = input("Enter monitoring interval in seconds [default: 30]: ").strip()
                if not interval:
                    interval = "30"
                interval = int(interval)
                print(f"Starting monitoring with {interval}s interval...")
                os.system(f"python start_monitoring.py --interval {interval}")
            except:
                print("Invalid interval, using default 30 seconds")
                os.system("python start_monitoring.py --interval 30")
                
        elif choice == "7":
            print(f"{Colors.OKBLUE}🎮 Launching Interactive Menu...{Colors.ENDC}")
            os.system("python cli_menu.py")
            
        elif choice == "8":
            print(f"{Colors.OKBLUE}⚙️ Opening Configuration Setup...{Colors.ENDC}")
            if os.name == 'nt':
                os.system("copy env.example .env & notepad .env")
            else:
                os.system("cp env.example .env && nano .env")
            print("Please restart the application after configuration")
            
        elif choice == "9":
            print(f"{Colors.OKBLUE}📋 Opening Commands Guide...{Colors.ENDC}")
            if os.name == 'nt':
                os.system("type COMMANDS_GUIDE.md | more")
            else:
                os.system("less COMMANDS_GUIDE.md")
                
        elif choice == "0":
            print(f"{Colors.OKGREEN}👋 Thank you for using NULL Security System!{Colors.ENDC}")
            sys.exit(0)
            
        else:
            print(f"{Colors.FAIL}❌ Invalid choice! Please run again and select 0-9{Colors.ENDC}")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Program interrupted by user{Colors.ENDC}")
        sys.exit(0)

if __name__ == "__main__":
    main()