#!/usr/bin/env python3
"""Test untuk memastikan AI response tidak terpotong"""

from utils import get_gemini_suggestion

def test_full_response():
    print("=== TESTING AI RESPONSE COMPLETENESS ===")
    
    test_data = """SSH service running on port 22
Root login enabled
Password authentication enabled
Failed login attempts: 15 in last hour
No fail2ban configured
SSH version: OpenSSH 7.4
Weak ciphers enabled
No key-based authentication
Multiple admin accounts found
Sudo permissions: ALL=(ALL) NOPASSWD"""
    
    print("Input data length:", len(test_data))
    print("\nRequesting AI analysis...")
    
    result = get_gemini_suggestion('SSH Security Critical Test', test_data)
    
    print("\n" + "="*60)
    print("AI ANALYSIS RESULT:")
    print("="*60)
    print(result)
    print("="*60)
    
    print(f"\nAnalysis Statistics:")
    print(f"Total characters: {len(result)}")
    print(f"Total words: {len(result.split())}")
    print(f"Total lines: {len(result.splitlines())}")
    
    if result.strip():
        last_char = result.strip()[-1]
        print(f"Ends with: '{last_char}'")
        
        # Check for proper ending
        proper_endings = ['.', '!', '?', ':', ')']
        if last_char in proper_endings:
            print("✅ Response appears complete (ends properly)")
        else:
            print("⚠️ Response might be truncated (doesn't end properly)")
    else:
        print("❌ Empty response")
    
    # Check for truncation indicators
    truncation_indicators = ['...', '[...', '<truncated>', 'terpotong']
    is_truncated = any(indicator in result.lower() for indicator in truncation_indicators)
    
    if is_truncated:
        print("⚠️ Truncation indicators found")
    else:
        print("✅ No obvious truncation indicators")

if __name__ == "__main__":
    test_full_response()