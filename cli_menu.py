#!/usr/bin/env python3
"""
NULL Security System - Interactive CLI Menu
Modul ini menyediakan antarmuka CLI interaktif.
Dipanggil oleh launcher.py — JANGAN jalankan file ini langsung.
"""

import os
import sys
from utils import Colors, print_success, print_info, print_warning, print_danger, ensure_sudo_access

def display_banner():
    """Display ASCII art banner"""
    banner = f"""{Colors.OKBLUE}{Colors.BOLD}
 ███╗   ██╗██╗   ██╗██╗     ██╗          ███████╗███████╗ ██████╗
 ████╗  ██║██║   ██║██║     ██║          ██╔════╝██╔════╝██╔════╝
 ██╔██╗ ██║██║   ██║██║     ██║          ███████╗█████╗  ██║     
 ██║╚██╗██║██║   ██║██║     ██║          ╚════██║██╔══╝  ██║     
 ██║ ╚████║╚██████╔╝███████╗███████╗     ███████║███████╗╚██████╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝     ╚══════╝╚══════╝ ╚═════╝
{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}            🛡️  INTEGRATED CYBERSECURITY SCANNER  🛡️{Colors.ENDC}
{Colors.OKGREEN}        🔍 White-box Security Assessment (On-demand)                   {Colors.ENDC}
{Colors.WARNING}                    ⚡ Powered by Local AI Analysis ⚡{Colors.ENDC}
"""
    print(banner)

def display_system_info():
    """Display system information"""
    print(f"{Colors.OKBLUE}{'='*75}{Colors.ENDC}")
    print(f"{Colors.BOLD}📊 SYSTEM INFO:{Colors.ENDC}")
    
    try:
        import platform
        import psutil
        
        print(f"   🖥️  OS: {platform.system()} {platform.release()}")
        print(f"   💻 Architecture: {platform.machine()}")
        print(f"   🧠 CPU Usage: {psutil.cpu_percent()}%")
        print(f"   📊 Memory Usage: {psutil.virtual_memory().percent}%")
        
        # Check Telegram config & Load Env
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check AI status
        try:
            import requests
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            if ollama_url.endswith("/"):
                api_url = f"{ollama_url}api/tags"
            else:
                api_url = f"{ollama_url}/api/tags"
            response = requests.get(api_url, timeout=2)
            if response.status_code == 200:
                print(f"   🤖 Ollama AI: {Colors.OKGREEN}ONLINE{Colors.ENDC}")
            else:
                print(f"   🤖 Ollama AI: {Colors.WARNING}OFFLINE{Colors.ENDC}")
        except:
            print(f"   🤖 Ollama AI: {Colors.FAIL}OFFLINE{Colors.ENDC}")
        
        telegram_configured = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        if telegram_configured:
            print(f"   📱 Telegram: {Colors.OKGREEN}CONFIGURED{Colors.ENDC}")
        else:
            print(f"   📱 Telegram: {Colors.WARNING}NOT CONFIGURED{Colors.ENDC}")
            
    except Exception as e:
        print(f"   ⚠️  System info unavailable: {e}")
    
    print(f"{Colors.OKBLUE}{'='*75}{Colors.ENDC}")

def display_menu():
    """Display main menu options"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🎯 PILIH MODE SCANNING:{Colors.ENDC}")
    print(f"""
{Colors.OKGREEN}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.OKGREEN}│                        🔍 WHITE-BOX SECURITY                        │{Colors.ENDC}
{Colors.OKGREEN}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[1]{Colors.ENDC} ⚡ Quick Security Check        - Essential security validation  
  {Colors.BOLD}[2]{Colors.ENDC} 🔐 SSH Security Analysis       - SSH configuration assessment
  {Colors.BOLD}[3]{Colors.ENDC} 👥 User & Permission Audit     - Account security analysis
  {Colors.BOLD}[4]{Colors.ENDC} 🌐 Network Security Scan       - Port & service analysis
  {Colors.BOLD}[5]{Colors.ENDC} 🛡️  System Hardening Check     - Security hardening status

{Colors.WARNING}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.WARNING}│                        🎯 BLACK-BOX SECURITY                        │{Colors.ENDC}
{Colors.WARNING}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[6]{Colors.ENDC} 🔍 Detect Nmap            - Scan for Nmap activities
  {Colors.BOLD}[7]{Colors.ENDC} ☢️  Detect Nuclei          - Scan for Nuclei activities
  {Colors.BOLD}[8]{Colors.ENDC} 🚀 Detect FFUF           - Scan for FFUF activities

{Colors.OKBLUE}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.OKBLUE}│                       ⚙️ CONFIGURATION & TOOLS                     │{Colors.ENDC}
{Colors.OKBLUE}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
    {Colors.BOLD}[9]{Colors.ENDC} ⚙️  Setup Configuration    - Configure Telegram & AI
    {Colors.BOLD}[10]{Colors.ENDC} 🤖 Test AI Connection     - Verify Ollama AI setup
    {Colors.BOLD}[11]{Colors.ENDC} 📱 Test Telegram Bot      - Verify notification setup
    {Colors.BOLD}[12]{Colors.ENDC} 📋 View Commands Guide     - Show all available commands
    
{Colors.HEADER}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.HEADER}│                        👀 SERVER LOG MONITORING                     │{Colors.ENDC}
{Colors.HEADER}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
    {Colors.BOLD}[13]{Colors.ENDC} 📜 Tail Nginx Access Log  - View real-time web access
    {Colors.BOLD}[14]{Colors.ENDC} 📜 Tail Nginx Error Log   - View real-time web errors
    {Colors.BOLD}[15]{Colors.ENDC} 📜 Tail Auth Log          - View real-time SSH logins

{Colors.HEADER}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.HEADER}│                          🚪 EXIT OPTIONS                            │{Colors.ENDC}
{Colors.HEADER}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}
  {Colors.BOLD}[0]{Colors.ENDC} 🚪 Exit Program                - Keluar dari aplikasi
""")

def execute_choice(choice):
    """Execute user's menu choice"""
    
    if choice == "1":
        print_info("⚡ Starting Quick Security Check...")
        print("Pilih quick check:")
        print("  [a] SSH + User Check")
        print("  [b] Network + Port Check") 
        print("  [c] System + Hardening Check")
        sub_choice = input("Pilihan [a/b/c]: ").strip().lower()
        
        if sub_choice == "a":
            os.system("python -m checkers.ssh_checker && python -m checkers.user_group_checker")
        elif sub_choice == "b":
            os.system("python -m checkers.network_config_checker && python -m core.port_scanner")
        elif sub_choice == "c":
            ensure_sudo_access()
            os.system("python -m checkers.system_info_checker && python -m checkers.hardening_checker")
        else:
            print_warning("Invalid choice, running basic system check...")
            os.system("python -m checkers.system_info_checker")
            
    elif choice == "2":
        print_info("🔐 Starting SSH Security Analysis...")
        os.system("python -m checkers.ssh_checker")
        
    elif choice == "3":
        print_info("👥 Starting User & Permission Audit...")
        os.system("python -m checkers.user_group_checker")
        
    elif choice == "4":
        print_info("🌐 Starting Network Security Scan...")
        os.system("python -m checkers.network_config_checker && python -m core.port_scanner")
        
    elif choice == "5":
        print_info("🛡️ Starting System Hardening Check...")
        ensure_sudo_access()
        os.system("python -m checkers.hardening_checker")
        
    elif choice == "6":
        print_info("🔍 Starting Nmap Detection...")
        os.system("python -m checkers.blackbox_checker --tool nmap")

    elif choice == "7":
        print_info("☢️ Starting Nuclei Detection...")
        os.system("python -m checkers.blackbox_checker --tool nuclei")

    elif choice == "8":
        print_info("🚀 Starting FFUF Detection...")
        os.system("python -m checkers.blackbox_checker --tool ffuf")

    elif choice == "9":
        print_info("⚙️ Opening Configuration Setup...")
        if os.name == 'nt':
            os.system("notepad .env")
        else:
            os.system("nano .env")
        print_info("Configuration saved. Please restart the application.")
        
    elif choice == "10":
        print_info("🤖 Testing AI Connection...")
        try:
            from utils import get_ollama_suggestion
            result = get_ollama_suggestion("Test Connection", "Connection test for Ollama AI")
            if "TIMEOUT" not in result and "ERROR" not in result:
                print_success("✅ Ollama AI connection successful!")
            else:
                print_warning("⚠️ Ollama AI connection issues detected")
        except Exception as e:
            print_danger(f"❌ AI connection failed: {e}")
            
    elif choice == "11":
        print_info("📱 Testing Telegram Bot...")
        try:
            from utils import send_to_telegram
            send_to_telegram("Connection Test", "System OK", "Telegram bot connection test successful! 🎉")
            print_success("✅ Telegram notification sent successfully!")
        except Exception as e:
            print_danger(f"❌ Telegram connection failed: {e}")
            
    elif choice == "12":
        print_info("📋 Opening Commands Guide...")
        if os.name == 'nt':
            os.system("type docs\\COMMANDS_GUIDE.md | more")
        else:
            os.system("less docs/COMMANDS_GUIDE.md")

    elif choice == "13":
        print_info("📜 Real-time Nginx Access Log (Press Ctrl+C to exit)...")
        if os.name == 'nt':
            print_warning("Perintah tail tidak didukung secara native di Windows.")
        else:
            os.system("tail -f /var/log/nginx/access.log")

    elif choice == "14":
        print_info("📜 Real-time Nginx Error Log (Press Ctrl+C to exit)...")
        if os.name == 'nt':
            print_warning("Perintah tail tidak didukung secara native di Windows.")
        else:
            os.system("tail -f /var/log/nginx/error.log")

    elif choice == "15":
        print_info("📜 Real-time Auth Log (Press Ctrl+C to exit)...")
        if os.name == 'nt':
            print_warning("Perintah tail tidak didukung secara native di Windows.")
        else:
            os.system("tail -f /var/log/auth.log")
            
    elif choice == "0":
        print_success("👋 Terima kasih telah menggunakan NULL Security System!")
        sys.exit(0)
        
    else:
        print_danger("❌ Invalid choice! Please select 0-15")

def main():
    """Main interactive CLI function"""
    try:
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Display banner and info
            display_banner()
            display_system_info()
            display_menu()
            
            # Get user choice
            choice = input(f"\n{Colors.BOLD}Pilih opsi [0-15]: {Colors.ENDC}").strip()
            
            if choice:
                print(f"\n{Colors.OKBLUE}{'='*75}{Colors.ENDC}")
                execute_choice(choice)
                
                # Wait for user before returning to menu
                input(f"\n{Colors.BOLD}Press Enter to return to main menu...{Colors.ENDC}")
            else:
                print_warning("Please enter a valid choice!")
                
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Program interrupted by user{Colors.ENDC}")
        print_success("👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print_danger(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"{Colors.WARNING}⚠️  Jalankan program melalui launcher.py, bukan file ini.{Colors.ENDC}")
    print(f"{Colors.OKBLUE}   Gunakan: python launcher.py{Colors.ENDC}")
