#!/usr/bin/env python3
"""
Emergency Ubuntu Server Fix - Ultra Conservative Settings
For extremely slow Ubuntu servers that timeout even at 60s
"""

import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

def test_minimal_generation():
    """Test with absolutely minimal settings"""
    print("🐧 Emergency Ubuntu Test - Ultra Minimal Settings")
    print("=" * 50)

    if not OLLAMA_MODEL:
        print("❌ OLLAMA_MODEL belum diset di .env")
        return False, 0
    
    # Ultra minimal request
    data = {
        "model": OLLAMA_MODEL,
        "prompt": "OK",  # Single word prompt
        "stream": False,
        "options": {
            "temperature": 0.1,    # Minimal creativity
            "num_predict": 5,      # Just 5 tokens max
            "num_ctx": 64,         # Tiny context
            "top_k": 1,            # Only best choice
            "top_p": 0.1,          # Very focused
            "seed": 42,
            "repeat_penalty": 1.0
        }
    }
    
    print("Testing ultra-minimal generation...")
    print("Request siap (model diambil dari OLLAMA_MODEL)")
    
    start_time = time.time()
    
    try:
        # Start with very long timeout for first test
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                               json=data, 
                               timeout=120)  # 2 minutes
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('response', '').strip()
            print(f"✅ SUCCESS in {duration:.1f}s")
            print(f"Output: '{output}'")
            return True, duration
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False, duration
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ TIMEOUT after {duration:.1f}s")
        return False, duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ ERROR after {duration:.1f}s: {e}")
        return False, duration

def check_server_resources():
    """Check server performance indicators"""
    print("\n🔍 Server Resource Check:")
    
    import subprocess
    
    try:
        # Check memory
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print("Memory:", result.stdout.strip().split('\n')[1])
    except:
        print("Could not check memory")
    
    try:
        # Check load average
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip()
        print("Load average:", load)
    except:
        print("Could not check load")
    
    try:
        # Check Ollama process
        result = subprocess.run(['ps', 'aux', '|', 'grep', 'ollama'], 
                              shell=True, capture_output=True, text=True)
        lines = [l for l in result.stdout.split('\n') if 'ollama' in l and 'grep' not in l]
        if lines:
            print("Ollama process:", lines[0].split()[2:6])  # PID, CPU, MEM, TIME
    except:
        print("Could not check Ollama process")

def recommend_emergency_fix():
    """Provide emergency fix recommendations"""
    print("""
🚨 EMERGENCY UBUNTU SERVER FIX RECOMMENDATIONS:

1. **IMMEDIATE ACTIONS:**
   # Stop other services to free resources
   sudo systemctl stop apache2 nginx mysql postgresql
   
   # Restart Ollama with minimal settings
   sudo systemctl stop ollama
   export OLLAMA_NUM_PARALLEL=1
   export OLLAMA_MAX_LOADED_MODELS=1
   export OLLAMA_KEEP_ALIVE=1m
   sudo systemctl start ollama
   
    # Switch to smaller model if possible
    ollama pull <model-ringan>  # sesuaikan model ringan pilihan Anda

2. **SYSTEM OPTIMIZATION:**
   # Increase swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # Reduce system load
   sudo systemctl disable --now snapd
   sudo apt remove --purge snapd

3. **OLLAMA CONFIGURATION:**
   # Create optimized systemd override
   sudo mkdir -p /etc/systemd/system/ollama.service.d/
   echo '[Service]
   Environment="OLLAMA_NUM_PARALLEL=1"
   Environment="OLLAMA_MAX_LOADED_MODELS=1"
   Environment="OLLAMA_KEEP_ALIVE=30s"
   TimeoutStartSec=300
   TimeoutStopSec=60' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
   
   sudo systemctl daemon-reload
   sudo systemctl restart ollama

4. **ALTERNATIVE: Use Fallback-Only Mode**
   # Disable AI completely in .env
   DISABLE_AI_ANALYSIS=true
   
   # System will use only rule-based analysis

5. **SERVER UPGRADE CONSIDERATION:**
   Current server appears severely resource-constrained.
   Consider:
    - More RAM sesuai kebutuhan model pada OLLAMA_MODEL
   - Faster CPU/SSD
   - Or use cloud AI API instead of local Ollama
""")

if __name__ == "__main__":
    check_server_resources()
    
    success, duration = test_minimal_generation()
    
    if success:
        print(f"\n✅ Server can handle AI but very slow ({duration:.1f}s for minimal request)")
        print("Recommendation: Use extended timeouts (180s+) or switch to fallback mode")
    else:
        print(f"\n❌ Server cannot handle AI reliably (failed after {duration:.1f}s)")
        recommend_emergency_fix()
        
    print(f"\n📊 Performance Assessment:")
    if duration < 30:
        print("🟢 GOOD - Normal timeouts should work")
    elif duration < 60:
        print("🟡 SLOW - Need extended timeouts (90s+)")
    elif duration < 120:
        print("🟠 VERY SLOW - Need very long timeouts (180s+)")
    else:
        print("🔴 CRITICAL - Consider fallback-only mode")