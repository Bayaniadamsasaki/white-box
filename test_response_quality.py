#!/usr/bin/env python3

"""
Test script untuk menguji kualitas respons AI yang sudah dioptimasi
- Menguji panjang respons optimal (tidak terlalu panjang/pendek)
- Memastikan tidak ada truncation
- Memverifikasi format dan struktur respons
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def test_response_quality():
    """Test kualitas respons AI dengan berbagai skenario"""
    
    print("🔍 Testing AI Response Quality...")
    print("=" * 60)
    
    # Test cases dengan berbagai complexity
    test_cases = [
        {
            "name": "SSH Configuration Test",
            "output": """
SSH service is running on port 22
PasswordAuthentication yes
PermitRootLogin yes
Protocol 2
MaxAuthTries 6
            """,
            "expected_length": (200, 800)  # Min 200, Max 800 words
        },
        {
            "name": "Firewall Status Check", 
            "output": """
ufw: inactive
iptables: no rules configured
open ports: 22, 80, 443, 3306
            """,
            "expected_length": (200, 800)
        },
        {
            "name": "User Permission Analysis",
            "output": """
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
mysql:x:112:117:MySQL Server,,,:/nonexistent:/bin/false
User 'admin' has sudo privileges
            """,
            "expected_length": (200, 800)
        }
    ]
    
    print(f"🤖 Using Ollama model: {OLLAMA_MODEL}")
    print(f"🌐 Ollama endpoint: {OLLAMA_BASE_URL}")
    print()
    
    # Check Ollama connection
    try:
        health_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if health_response.status_code != 200:
            print("❌ Ollama tidak dapat diakses!")
            return False
        print("✅ Ollama connection OK")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        # Create prompt sesuai format baru
        prompt = f"""Sebagai security expert, analisis hasil tes keamanan berikut untuk '{test_case['name']}' dan berikan saran yang EFISIEN, FOKUS, dan LENGKAP.

Berikan respons dalam format berikut (maksimal 800 kata, minimum 200 kata):

**STATUS:** [AMAN/PERLU PERHATIAN/BERBAHAYA]

**TEMUAN:**
• [Poin kunci 1]
• [Poin kunci 2]
• [Poin kunci 3]

**REKOMENDASI:**
1. [Aksi utama 1]
2. [Aksi utama 2]
3. [Aksi utama 3]

**PRIORITAS:** [Urutan implementasi]

WAJIB: Respons harus LENGKAP sampai selesai, tidak boleh terpotong, dan fokus pada hal penting saja.

Nama Tes: {test_case['name']}
Hasil Tes:
{test_case['output']}

Analisis (lengkap sampai selesai):"""

        # Request dengan parameter optimal
        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.8,
                "num_predict": 1200,
                "num_ctx": 4096,
                "stop": ["**END**"],
                "repeat_penalty": 1.1,
                "seed": 42
            }
        }
        
        start_time = time.time()
        
        try:
            print("⏳ Processing... (may take 30-60 seconds)")
            response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                                   json=data, timeout=120)
            response.raise_for_status()
            
            end_time = time.time()
            duration = end_time - start_time
            
            response_json = response.json()
            if 'response' in response_json:
                suggestion = response_json['response'].strip()
                
                # Clean up DeepSeek thinking tags
                if '<think>' in suggestion:
                    think_end = suggestion.find('</think>')
                    if think_end != -1:
                        suggestion = suggestion[think_end + 8:].strip()
                
                # Analyze response quality
                word_count = len(suggestion.split())
                char_count = len(suggestion)
                
                # Check format compliance
                has_status = "**STATUS:**" in suggestion
                has_temuan = "**TEMUAN:**" in suggestion
                has_rekomendasi = "**REKOMENDASI:**" in suggestion
                has_prioritas = "**PRIORITAS:**" in suggestion
                
                # Check for truncation indicators
                is_truncated = (
                    suggestion.endswith('...') or
                    suggestion.endswith('ter') or
                    suggestion.endswith('men') or
                    not suggestion.endswith(('.', '!', '?', ':', ')')) or
                    char_count < 200
                )
                
                # Results
                print(f"⏱️ Response time: {duration:.1f}s")
                print(f"📊 Length: {char_count} chars, {word_count} words")
                print(f"📝 Format compliance:")
                print(f"   ✅ STATUS: {has_status}")
                print(f"   ✅ TEMUAN: {has_temuan}")
                print(f"   ✅ REKOMENDASI: {has_rekomendasi}")
                print(f"   ✅ PRIORITAS: {has_prioritas}")
                print(f"🔍 Truncation check: {'❌ TRUNCATED' if is_truncated else '✅ COMPLETE'}")
                
                # Length assessment
                min_len, max_len = test_case['expected_length']
                if char_count < min_len:
                    length_status = "❌ TOO SHORT"
                elif char_count > max_len:
                    length_status = "⚠️ TOO LONG"
                else:
                    length_status = "✅ OPTIMAL"
                
                print(f"📏 Length assessment: {length_status}")
                
                # Sample output
                print(f"\n📄 Sample output (first 200 chars):")
                print(f"'{suggestion[:200]}{'...' if len(suggestion) > 200 else ''}'")
                
                results.append({
                    'test': test_case['name'],
                    'duration': duration,
                    'char_count': char_count,
                    'word_count': word_count,
                    'is_complete': not is_truncated,
                    'has_proper_format': has_status and has_temuan and has_rekomendasi and has_prioritas,
                    'length_optimal': min_len <= char_count <= max_len
                })
                
            else:
                print("❌ Invalid response format")
                results.append({
                    'test': test_case['name'],
                    'error': 'Invalid response format'
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'test': test_case['name'],
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY RESULTS")
    print("=" * 60)
    
    successful_tests = [r for r in results if 'error' not in r]
    if successful_tests:
        avg_duration = sum(r['duration'] for r in successful_tests) / len(successful_tests)
        avg_length = sum(r['char_count'] for r in successful_tests) / len(successful_tests)
        complete_responses = sum(1 for r in successful_tests if r['is_complete'])
        proper_format = sum(1 for r in successful_tests if r['has_proper_format'])
        optimal_length = sum(1 for r in successful_tests if r['length_optimal'])
        
        print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
        print(f"⏱️ Average response time: {avg_duration:.1f}s")
        print(f"📊 Average length: {avg_length:.0f} characters")
        print(f"🔍 Complete responses: {complete_responses}/{len(successful_tests)}")
        print(f"📝 Proper format: {proper_format}/{len(successful_tests)}")
        print(f"📏 Optimal length: {optimal_length}/{len(successful_tests)}")
        
        # Overall assessment
        if complete_responses == len(successful_tests) and proper_format == len(successful_tests) and optimal_length >= len(successful_tests) * 0.8:
            print("\n🎉 OVERALL: EXCELLENT - All responses meet quality standards!")
        elif complete_responses >= len(successful_tests) * 0.8:
            print("\n✅ OVERALL: GOOD - Most responses meet quality standards")
        else:
            print("\n⚠️ OVERALL: NEEDS IMPROVEMENT - Some quality issues detected")
    else:
        print("❌ No successful tests completed")
    
    return len(successful_tests) > 0

if __name__ == "__main__":
    test_response_quality()