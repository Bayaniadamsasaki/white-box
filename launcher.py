#!/usr/bin/env python3
"""
NULL Security System - Quick Launcher
Simple banner dengan opsi white box dan blackbox
"""

import os
import sys
from utils import Colors, ensure_sudo_access

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

def wait_for_return():
    """Wait for user to press Enter to return to menu"""
    input(f"\n{Colors.OKGREEN}📤 Scan completed! Press Enter to return to main menu...{Colors.ENDC}")

def main():
    """Legacy quick launcher menu (kept for --quick mode)."""
    """Main launcher function with menu loop"""
    while True:
        try:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            show_banner()
            show_options()
            
            choice = input(f"\n{Colors.BOLD}Pilih opsi [0-9]: {Colors.ENDC}").strip()
            
            print(f"\n{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
            
            if choice == "0":
                print(f"{Colors.OKGREEN}🚪 Goodbye! Exiting NULL Security System...{Colors.ENDC}")
                break
                
            elif choice == "1":
                print(f"{Colors.OKGREEN}🔍 Starting White-box Full Security Scan...{Colors.ENDC}")
                os.system("python main_scanner.py")
                wait_for_return()
                
            elif choice == "2":
                print(f"{Colors.OKGREEN}⚡ Starting White-box Quick Security Check...{Colors.ENDC}")
                print("Quick checks available:")
                print("  [a] SSH + Users      [b] Network + Ports     [c] System + Hardening")
                sub = input("Choose [a/b/c] or Enter for all: ").strip().lower()
                
                if sub == "a":
                    os.system("python -m checkers.ssh_checker && python -m checkers.user_group_checker")
                elif sub == "b":
                    os.system("python -m checkers.network_config_checker && python -m core.port_scanner")
                elif sub == "c":
                    ensure_sudo_access()
                    os.system("python -m checkers.system_info_checker && python -m checkers.hardening_checker")
                else:
                    os.system("python -m checkers.ssh_checker && python -m checkers.user_group_checker && python -m checkers.system_info_checker")
                wait_for_return()
                    
            elif choice == "3":
                print(f"{Colors.OKGREEN}🔧 Individual Module Selection...{Colors.ENDC}")
                modules = [
                    ("python -m checkers.ssh_checker", "SSH Security"),
                    ("python -m checkers.user_group_checker", "User & Groups"),
                    ("python -m checkers.hardening_checker", "System Hardening"),
                    ("python -m checkers.web_checker", "Web Services"),
                    ("python -m core.port_scanner", "Port Scanning"),
                    ("python -m checkers.network_config_checker", "Network Config")
                ]
                
                print("Available modules:")
                for i, (script, desc) in enumerate(modules, 1):
                    print(f"  [{i}] {desc}")
                
                mod_choice = input("Select module [1-6]: ").strip()
                try:
                    idx = int(mod_choice) - 1
                    if 0 <= idx < len(modules):
                        command, desc = modules[idx]
                        if "hardening" in command:
                            ensure_sudo_access()
                        print(f"Running {desc}...")
                        os.system(command)
                        wait_for_return()
                    else:
                        print("Invalid module choice")
                        wait_for_return()
                except:
                    print("Invalid input")
                    wait_for_return()
                    
            elif choice == "4":
                print(f"{Colors.WARNING}🚨 Starting Black-box Real-time Attack Monitor...{Colors.ENDC}")
                print(f"{Colors.WARNING}⚠️  Press Ctrl+C to stop monitoring{Colors.ENDC}")
                os.system("python start_monitoring.py --continuous")
                wait_for_return()
                
            elif choice == "5":
                print(f"{Colors.WARNING}🔍 Starting Black-box Single Attack Scan...{Colors.ENDC}")
                os.system("python start_monitoring.py --single")
                wait_for_return()
                
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
                wait_for_return()
                    
            elif choice == "7":
                print(f"{Colors.OKBLUE}🎮 Launching Interactive Menu...{Colors.ENDC}")
                try:
                    from cli_menu import main as interactive_main
                    interactive_main()
                    break
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Gagal membuka Interactive Menu: {e}{Colors.ENDC}")
                    wait_for_return()
                
            elif choice == "8":
                print(f"{Colors.OKBLUE}⚙️ Opening Configuration Setup...{Colors.ENDC}")
                if os.name == 'nt':
                    os.system("copy env.example .env & notepad .env")
                else:
                    os.system("cp env.example .env && nano .env")
                print("Please restart the application after configuration")
                wait_for_return()
                
            elif choice == "9":
                print(f"{Colors.OKBLUE}📋 Opening Commands Guide...{Colors.ENDC}")
                if os.name == 'nt':
                    os.system("type docs\\COMMANDS_GUIDE.md | more")
                else:
                    os.system("less docs/COMMANDS_GUIDE.md")
                wait_for_return()
                    
            else:
                print(f"{Colors.FAIL}❌ Invalid choice! Please select 0-9{Colors.ENDC}")
                wait_for_return()
                
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Interrupted by user. Returning to menu...{Colors.ENDC}")
            continue
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            wait_for_return()

if __name__ == "__main__":
    # Default launcher langsung ke Interactive Menu agar tidak double CLI.
    # Gunakan `python launcher.py --quick` jika ingin menu launcher lama.
    if "--quick" in sys.argv:
        main()
    else:
        try:
            from cli_menu import main as interactive_main
            interactive_main()
        except Exception as e:
            print(f"{Colors.FAIL}❌ Gagal menjalankan Interactive Menu: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️ Menjalankan launcher mode lama sebagai fallback...{Colors.ENDC}")
            main()