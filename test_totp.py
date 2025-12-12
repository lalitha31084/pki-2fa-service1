import pyotp
import base64
import time
import binascii

def test_totp():
    print("--- Testing TOTP Generation ---")

    # 1. Read the decrypted seed (from our previous test)
    try:
        with open("decrypted_seed_test.txt", "r") as f:
            hex_seed = f.read().strip()
            print(f"Loaded Hex Seed: {hex_seed[:10]}...")
    except FileNotFoundError:
        print("Error: decrypted_seed_test.txt not found. Run test_decryption.py first.")
        return

    # 2. Convert Hex -> Base32 (CRITICAL STEP)
    try:
        # Convert hex string to raw bytes
        seed_bytes = bytes.fromhex(hex_seed)
        
        # Encode bytes to Base32 (required by TOTP libraries)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        print(f"Base32 Seed:     {base32_seed[:10]}...")
    except Exception as e:
        print(f"Error converting seed: {e}")
        return

    # 3. Generate TOTP
    # Standard settings: SHA-1, 6 digits, 30 second interval
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6, digest='sha1')
    
    current_code = totp.now()
    time_remaining = totp.interval - (int(time.time()) % totp.interval)

    print(f"\n✅ SUCCESS!")
    print(f"Current 2FA Code: {current_code}")
    print(f"Valid for:        {time_remaining} more seconds")

    # 4. Verification Test (Simulate the API verification)
    # verify() allows us to check the code. valid_window=1 means +/- 30 seconds tolerance.
    is_valid = totp.verify(current_code, valid_window=1)
    print(f"Verification Check: {'Passed' if is_valid else 'Failed'}")

if __name__ == "__main__":
    test_totp()