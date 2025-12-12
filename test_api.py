import requests
import json
import time

BASE_URL = "http://127.0.0.1:8080"

def test_api():
    print("--- Testing API Endpoints ---")

    # 1. Read Encrypted Seed from file
    try:
        with open("encrypted_seed.txt", "r") as f:
            encrypted_seed = f.read().strip()
    except FileNotFoundError:
        print("Error: encrypted_seed.txt not found!")
        return

    # --- TEST 1: Decrypt Seed ---
    print("\n1. Testing POST /decrypt-seed...")
    payload = {"encrypted_seed": encrypted_seed}
    try:
        response = requests.post(f"{BASE_URL}/decrypt-seed", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Failed to decrypt seed through API.")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Is the server running in the other terminal?")
        return

    # --- TEST 2: Generate 2FA ---
    print("\n2. Testing GET /generate-2fa...")
    code = None
    try:
        response = requests.get(f"{BASE_URL}/generate-2fa")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if "code" in data:
            code = data["code"]
            print(f"✅ Received Code: {code}")
        else:
            print("❌ No code received.")
            return
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return

    # --- TEST 3: Verify 2FA ---
    print("\n3. Testing POST /verify-2fa...")
    verify_payload = {"code": code}
    try:
        response = requests.post(f"{BASE_URL}/verify-2fa", json=verify_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.json().get("valid") is True:
            print("\n🎉 ALL SYSTEMS GO! API is working perfectly.")
        else:
            print("\n❌ Verification failed.")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()