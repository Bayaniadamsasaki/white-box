#!/usr/bin/env python3
"""
NULL Security System - Launcher
Satu-satunya entry point untuk menjalankan sistem.
Gunakan: python launcher.py
"""

import os
import sys
from utils import Colors

def show_banner():
    """Display the NULL Security System banner"""
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

if __name__ == "__main__":
    show_banner()
    try:
        from cli_menu import main as interactive_main
        interactive_main()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Gagal menjalankan menu: {e}{Colors.ENDC}")