#!/usr/bin/env python3
"""
Ollama Test & Setup Script
Script untuk test koneksi Ollama dan memastikan model sudah siap digunakan.
"""

import requests
import os
import json
from dotenv import load_dotenv
from utils import print_header, print_success, print_warning, print_danger, print_info

load_dotenv()

def test_ollama_connection():
    """Test koneksi ke Ollama server"""
    print_header("Testing Ollama Connection")
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
    
    try:
        # Test 1: Check if Ollama is running
        print_info("1. Checking if Ollama server is running...")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print_success("✓ Ollama server is running!")
            
            # Test 2: Check available models
            print_info("\n2. Checking available models...")
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            if available_models:
                print_success(f"✓ Found {len(available_models)} model(s):")
                for model in available_models:
                    if model_name in model or model.startswith(model_name.split(':')[0]):
                        print_success(f"  ✓ {model} (CONFIGURED)")
                    else:
                        print_info(f"  • {model}")
            else:
                print_warning("⚠ No models found in Ollama")
                
            # Test 3: Check if configured model exists
            print_info(f"\n3. Checking if configured model '{model_name}' is available...")
            model_exists = any(model_name in model or model.startswith(model_name.split(':')[0]) 
                             for model in available_models)
            
            if model_exists:
                print_success(f"✓ Model '{model_name}' is available!")
                
                # Test 4: Test model inference
                print_info("\n4. Testing model inference...")
                test_prompt = "Jelaskan singkat apa itu keamanan siber dalam 1 kalimat."
                
                test_data = {
                    "model": model_name,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 100
                    }
                }
                
                inference_response = requests.post(f"{ollama_url}/api/generate", 
                                                 json=test_data, timeout=30)
                
                if inference_response.status_code == 200:
                    result = inference_response.json()
                    if 'response' in result:
                        print_success("✓ Model inference test successful!")
                        print_info(f"Sample response: {result['response'][:100]}...")
                        return True
                    else:
                        print_warning("⚠ Model responded but no 'response' field found")
                        return False
                else:
                    print_danger(f"✗ Model inference failed: {inference_response.status_code}")
                    return False
            else:
                print_danger(f"✗ Model '{model_name}' not found!")
                print_info("\nAvailable options:")
                print_info("1. Pull the model: ollama pull deepseek-r1:8b")
                print_info("2. Or change OLLAMA_MODEL in .env to one of the available models")
                return False
                
        else:
            print_danger(f"✗ Ollama server not responding: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_danger("✗ Cannot connect to Ollama server!")
        print_info("Solutions:")
        print_info("1. Start Ollama: ollama serve")
        print_info("2. Check if port 11434 is available")
        print_info("3. Verify OLLAMA_BASE_URL in .env")
        return False
        
    except requests.exceptions.Timeout:
        print_danger("✗ Connection timeout!")
        print_info("Ollama might be starting up or overloaded")
        return False
        
    except Exception as e:
        print_danger(f"✗ Unexpected error: {e}")
        return False

def setup_ollama_model():
    """Setup script untuk download model jika belum ada"""
    print_header("Ollama Model Setup")
    
    model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
    print_info(f"Setting up model: {model_name}")
    
    try:
        import subprocess
        print_info("Attempting to pull model via ollama CLI...")
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_success(f"✓ Model '{model_name}' pulled successfully!")
            return True
        else:
            print_danger(f"✗ Failed to pull model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_danger("✗ Timeout while pulling model (>5 minutes)")
        return False
    except FileNotFoundError:
        print_danger("✗ 'ollama' command not found in PATH")
        print_info("Install Ollama from: https://ollama.ai/")
        return False
    except Exception as e:
        print_danger(f"✗ Error pulling model: {e}")
        return False

def main():
    print_header("NULL Security - Ollama Integration Test")
    
    # Test current connection
    if test_ollama_connection():
        print_header("Ollama Setup Complete", char="=", color_code="\033[92m")
        print_success("🎉 Ollama is ready to use!")
        print_info("You can now run the security scanner with Ollama AI analysis")
        print_info("Commands:")
        print_info("  python main_scanner.py")
        print_info("  python start_monitoring.py --continuous")
    else:
        print_header("Setup Required", char="=", color_code="\033[93m")
        
        choice = input("\nWould you like to try pulling the model? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            if setup_ollama_model():
                print_info("\nRetesting connection...")
                if test_ollama_connection():
                    print_success("🎉 Setup complete! Ollama is now ready.")
                else:
                    print_danger("Setup completed but still having issues")
            else:
                print_danger("Model setup failed")
        else:
            print_info("Please ensure Ollama is running and the model is available")

if __name__ == "__main__":
    main()