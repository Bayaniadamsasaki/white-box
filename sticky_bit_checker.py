"""Modul untuk memeriksa direktori yang world-writable dengan sticky bit.

Sticky bit pada direktori world-writable (seperti /tmp atau /var/tmp) adalah
pengaturan keamanan penting. Ini memastikan bahwa pengguna hanya dapat menghapus
atau mengganti nama file yang mereka miliki di dalam direktori tersebut, meskipun
direktori itu sendiri dapat ditulis oleh semua orang. Modul ini mencari direktori
dengan izin `drwxrwxrwt` (1777) atau serupa.
"""
import os
import stat
from utils import (
    print_info, print_success, print_warning, print_danger, print_header,
    send_to_telegram, get_gemini_suggestion,
    capture_command_output
)

COMMON_STICKY_DIRS = ["/tmp", "/var/tmp"]

def check_directory_sticky_bit(dir_path):
    """Menganalisis izin sebuah direktori untuk sticky bit dan world-writable."""
    analysis_result = {"path": dir_path, "exists": False, "is_dir": False, "is_world_writable": False, "has_sticky_bit": False, "is_secure": None, "notes": ""}
    try:
        if not os.path.exists(dir_path):
            analysis_result["notes"] = f"Direktori {dir_path} tidak ditemukan."
            return analysis_result
        analysis_result["exists"] = True

        if not os.path.isdir(dir_path):
            analysis_result["notes"] = f"{dir_path} bukan direktori."
            return analysis_result
        analysis_result["is_dir"] = True
        
        mode = os.stat(dir_path).st_mode
        
        is_world_writable = bool(mode & stat.S_IWOTH)
        analysis_result["is_world_writable"] = is_world_writable
        
        # Periksa sticky bit: S_ISVTX
        has_sticky_bit = bool(mode & stat.S_ISVTX)
        analysis_result["has_sticky_bit"] = has_sticky_bit
        
        permissions_octal = oct(stat.S_IMODE(mode))
        analysis_result["notes"] = f"Izin untuk {dir_path}: {permissions_octal}. World-writable: {is_world_writable}, Sticky bit: {has_sticky_bit}."

        if is_world_writable:
            if has_sticky_bit:
                analysis_result["is_secure"] = True
                s_msg = f"GOOD: Direktori world-writable {dir_path} memiliki sticky bit ({permissions_octal})."
                
                analysis_result["notes"] += f"\n   {s_msg}"
            else:
                analysis_result["is_secure"] = False
                d_msg = f"DANGER: Direktori world-writable {dir_path} TIDAK memiliki sticky bit ({permissions_octal})! Ini adalah risiko keamanan."
                
                analysis_result["notes"] += f"\n   {d_msg}"
        else:
            
            analysis_result["is_secure"] = True
            i_msg = f"INFO: Direktori {dir_path} tidak world-writable ({permissions_octal}). Sticky bit (saat ini: {has_sticky_bit}) kurang kritikal dalam konteks ini."

            analysis_result["notes"] += f"\n   {i_msg}"
            
    except Exception as e:
        err_msg = f"Gagal memeriksa direktori {dir_path}: {e}"
        
        analysis_result["notes"] = err_msg
        analysis_result["is_secure"] = False
    return analysis_result

def run_sticky_bit_checks():
    """Menjalankan pemeriksaan untuk direktori world-writable dengan sticky bit."""
    test_name = "Pemeriksaan Sticky Bit pada Direktori World-Writable"
    print_header(test_name)
    all_raw_outputs = []
    analysis_reports = []

    # Periksa direktori umum
    for dir_to_check in COMMON_STICKY_DIRS:
        result = check_directory_sticky_bit(dir_to_check)
        
        if result["notes"]:
            
            if result["exists"] and result["is_dir"]:
                if result["is_world_writable"] and not result["has_sticky_bit"]:
                    print_danger(f"Tes '{test_name}' untuk '{result['path']}': Ditemukan world-writable tanpa sticky bit.")
                else:
                    print_success(f"Tes '{test_name}' untuk '{result['path']}': Status OK atau tidak world-writable.")
            elif not result["exists"]:
                print_warning(f"Tes '{test_name}': Direktori '{result['path']}' tidak ditemukan.")
            elif not result["is_dir"]:
                print_warning(f"Tes '{test_name}': Path '{result['path']}' bukan direktori.")
            
            analysis_reports.append(result["notes"])
    
    find_command_note = (r"Catatan: Untuk pemeriksaan yang lebih komprehensif, Anda dapat menjalankan perintah seperti:\n" 
                          r"`find / -xdev -type d \\( -perm -0002 -a ! -perm -1000 \\) -print 2>/dev/null` \n"
                          r"untuk menemukan semua direktori world-writable tanpa sticky bit di filesystem lokal.\n" 
                          r"Modul ini saat ini hanya memeriksa direktori umum yang diketahui.")
    print_info(find_command_note)
    all_raw_outputs.append(find_command_note)

    if analysis_reports:
        all_raw_outputs.append("\n--- Hasil Analisis Sticky Bit (Direktori Umum) ---")
        all_raw_outputs.extend(analysis_reports)
    else:
        all_raw_outputs.append("Tidak ada analisis spesifik yang dihasilkan untuk direktori umum (mungkin semua tidak ada atau error).")

    combined_raw_output = "\n".join(filter(None, all_raw_outputs))

    if not combined_raw_output.strip():
        print_info("Tidak ada data laporan yang signifikan dihasilkan dari pemeriksaan sticky bit.")
        combined_raw_output = "Tidak ada data laporan yang signifikan dihasilkan dari pemeriksaan sticky bit."

    gemini_saran = get_gemini_suggestion(test_name, combined_raw_output)
    
    send_to_telegram(test_name, combined_raw_output, gemini_saran)

if __name__ == '__main__':
    run_sticky_bit_checks()