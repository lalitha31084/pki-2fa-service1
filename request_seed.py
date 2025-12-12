import requests
import json
import os

# API Endpoint from instructions
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def get_seed():
    print("--- Requesting Encrypted Seed ---")
    
    # 1. Get User Inputs
    student_id = input("Enter your Student ID: ").strip()
    repo_url = input("Enter your GitHub Repo URL (exact): ").strip()
    
    if not student_id or not repo_url:
        print("Error: Student ID and Repo URL are required.")
        return

    # 2. Read Public Key
    try:
        with open("student_public.pem", "r") as f:
            public_key = f.read()
    except FileNotFoundError:
        print("Error: student_public.pem not found. Did you run generate_keys.py?")
        return

    # 3. Prepare Payload
    # The requests library automatically handles JSON escaping (newlines become \n)
    payload = {
        "student_id": student_id,
        "github_repo_url": repo_url,
        "public_key": public_key
    }

    print("\nSending request to Instructor API...")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "encrypted_seed" in data:
                # Save the seed exactly as received
                seed_content = data["encrypted_seed"]
                with open("encrypted_seed.txt", "w") as f:
                    f.write(seed_content)
                print("\nSUCCESS! Seed saved to 'encrypted_seed.txt'")
                print(f"Seed preview: {seed_content[:20]}...")
            else:
                print("Error: Response did not contain 'encrypted_seed'")
                print(data)
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_seed()