#!/usr/bin/env python3

"""
Quick test untuk memverifikasi konfigurasi respons AI yang optimal
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def quick_test():
    print("🔥 Quick Response Quality Test")
    print("=" * 50)
    
    # Simple test case
    prompt = """Sebagai security expert, analisis hasil tes keamanan berikut untuk 'SSH Test' dan berikan saran yang EFISIEN, FOKUS, dan LENGKAP.

Berikan respons dalam format berikut (maksimal 800 kata, minimum 200 kata):

**STATUS:** [AMAN/PERLU PERHATIAN/BERBAHAYA]

**TEMUAN:**
• [Poin kunci 1]
• [Poin kunci 2]

**REKOMENDASI:**
1. [Aksi utama 1]
2. [Aksi utama 2]

**PRIORITAS:** [Urutan implementasi]

WAJIB: Respons harus LENGKAP sampai selesai, tidak boleh terpotong, dan fokus pada hal penting saja.

Nama Tes: SSH Test
Hasil Tes:
SSH port 22 open
PasswordAuthentication yes
PermitRootLogin yes

Analisis (lengkap sampai selesai):"""

    # Warm-up request dengan parameter ringan
    data = {
        "model": OLLAMA_MODEL,
        "prompt": "Hello, are you ready?",
        "stream": False,
        "options": {
            "num_predict": 50
        }
    }
    
    print("🔥 Warming up model...")
    try:
        warmup = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=data, timeout=30)
        if warmup.status_code == 200:
            print("✅ Model warmed up")
        else:
            print("⚠️ Warmup failed but continuing...")
    except:
        print("⚠️ Warmup timeout but continuing...")
    
    # Main test dengan konfigurasi optimal
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.8,
            "num_predict": 1200,
            "num_ctx": 4096,
            "repeat_penalty": 1.1,
            "seed": 42
        }
    }
    
    print("\n🧪 Testing optimized response...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                               json=data, timeout=90)
        response.raise_for_status()
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = response.json()
        if 'response' in result:
            suggestion = result['response'].strip()
            
            # Clean thinking tags
            if '<think>' in suggestion:
                think_end = suggestion.find('</think>')
                if think_end != -1:
                    suggestion = suggestion[think_end + 8:].strip()
            
            # Analysis
            char_count = len(suggestion)
            word_count = len(suggestion.split())
            
            # Format check
            has_status = "**STATUS:**" in suggestion
            has_temuan = "**TEMUAN:**" in suggestion  
            has_rekomendasi = "**REKOMENDASI:**" in suggestion
            has_prioritas = "**PRIORITAS:**" in suggestion
            
            # Truncation check
            is_complete = (
                suggestion.endswith(('.', '!', '?', ':')) and
                char_count >= 200 and
                not suggestion.endswith(('ter', 'men', 'kan', 'dan'))
            )
            
            print(f"⏱️ Response time: {duration:.1f}s")
            print(f"📊 Length: {char_count} chars, {word_count} words")
            print(f"📝 Format: STATUS={has_status}, TEMUAN={has_temuan}, REKOMENDASI={has_rekomendasi}, PRIORITAS={has_prioritas}")
            print(f"✅ Complete: {is_complete}")
            
            # Length assessment
            if 200 <= char_count <= 800:
                print("✅ Length: OPTIMAL")
            elif char_count < 200:
                print("❌ Length: TOO SHORT")
            else:
                print("⚠️ Length: TOO LONG")
            
            print("\n📄 Response preview:")
            print("-" * 30)
            print(suggestion[:300] + ("..." if len(suggestion) > 300 else ""))
            print("-" * 30)
            
            if has_status and has_temuan and has_rekomendasi and is_complete:
                print("\n🎉 HASIL: OPTIMAL - Respons AI memenuhi semua kriteria!")
            else:
                print("\n⚠️ HASIL: PERLU PERBAIKAN")
                
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()