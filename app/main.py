import os
import sys
import base64
import time
import logging
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

# --- Configuration ---
app = FastAPI(title="PKI 2FA Microservice")

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File Paths
# logic: If on Windows (Local test), use local 'data' folder. 
# If on Linux (Docker), use strict '/data' from instructions.
if sys.platform == "win32":
    DATA_DIR = os.path.join(os.getcwd(), "data")
else:
    DATA_DIR = "/data"

SEED_FILE = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_FILE = "student_private.pem"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Pydantic Models (Input Validation) ---
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# --- Helper Functions ---
def load_private_key():
    try:
        with open(PRIVATE_KEY_FILE, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
    except FileNotFoundError:
        logger.error(f"Private key not found at {PRIVATE_KEY_FILE}")
        return None

def get_totp_object(hex_seed: str):
    try:
        # Convert hex -> bytes -> base32
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        # Create TOTP object (SHA1, 6 digits, 30s)
        return pyotp.TOTP(base32_seed, interval=30, digits=6, digest='sha1')
    except Exception as e:
        logger.error(f"Error creating TOTP object: {e}")
        return None

# --- API Endpoints ---

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: DecryptRequest):
    """
    Decrypts the base64 encrypted seed using the private key 
    and saves it to storage.
    """
    private_key = load_private_key()
    if not private_key:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Private key missing")

    try:
        # 1. Decode Base64
        encrypted_data = base64.b64decode(request.encrypted_seed)

        # 2. Decrypt using RSA/OAEP + SHA256
        decrypted_bytes = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        decrypted_seed = decrypted_bytes.decode('utf-8')

        # 3. Validate Format (Must be 64 char hex)
        if len(decrypted_seed) != 64:
             raise ValueError("Decrypted seed is not 64 characters")
        
        # 4. Save to Persistent Storage
        with open(SEED_FILE, "w") as f:
            f.write(decrypted_seed)
            
        logger.info("Seed decrypted and saved successfully.")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        # Return 500 as per requirements
        return Response(content='{"error": "Decryption failed"}', status_code=500, media_type="application/json")

@app.get("/generate-2fa")
async def generate_2fa():
    """
    Reads the stored seed and generates the current TOTP code.
    """
    if not os.path.exists(SEED_FILE):
        return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        
        totp = get_totp_object(hex_seed)
        if not totp:
            raise ValueError("Invalid seed format")

        code = totp.now()
        # Calculate remaining seconds
        valid_for = totp.interval - (int(time.time()) % totp.interval)

        return {"code": code, "valid_for": valid_for}

    except Exception as e:
        logger.error(f"Generation error: {e}")
        return Response(content='{"error": "Generation failed"}', status_code=500, media_type="application/json")

@app.post("/verify-2fa")
async def verify_2fa(request: VerifyRequest):
    """
    Verifies a provided code against the stored seed.
    """
    if not request.code:
         raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_FILE):
        return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        
        totp = get_totp_object(hex_seed)
        
        # Verify with window=1 (±30 seconds tolerance)
        is_valid = totp.verify(request.code, valid_window=1)
        
        return {"valid": is_valid}

    except Exception as e:
        logger.error(f"Verification error: {e}")
        return Response(content='{"error": "Verification failed"}', status_code=500, media_type="application/json")