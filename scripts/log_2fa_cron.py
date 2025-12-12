#!/usr/bin/env python3
import os
import sys
import datetime
import base64
import pyotp

# Define paths (Docker absolute paths)
SEED_FILE = "/data/seed.txt"
LOG_FILE = "/cron/last_code.txt"

def log_2fa():
    # 1. Read Seed
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        print(f"[{datetime.datetime.now()}] Error: Seed file not found.")
        return

    # 2. Generate TOTP
    try:
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed, interval=30, digits=6, digest='sha1')
        code = totp.now()
        
        # 3. Log with UTC Timestamp
        # Format: YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp} - 2FA Code: {code}\n"
        
        # Append to log file
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
            
        print(f"Logged: {log_entry.strip()}")

    except Exception as e:
        print(f"Error generating code: {e}")

if __name__ == "__main__":
    log_2fa()