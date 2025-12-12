import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_test():
    print("--- Testing Decryption ---")

    # 1. Load Your Private Key
    print("Loading private key...")
    try:
        with open("student_private.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
    except FileNotFoundError:
        print("Error: student_private.pem not found.")
        return

    # 2. Load the Encrypted Seed
    print("Loading encrypted seed...")
    try:
        with open("encrypted_seed.txt", "r") as seed_file:
            encrypted_data_b64 = seed_file.read().strip()
    except FileNotFoundError:
        print("Error: encrypted_seed.txt not found.")
        return
    
    # 3. Decrypt
    try:
        # Decode Base64 first
        encrypted_data = base64.b64decode(encrypted_data_b64)

        # RSA Decryption with OAEP and SHA-256 (Specific Requirement)
        decrypted_bytes = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Convert bytes to string
        decrypted_seed = decrypted_bytes.decode('utf-8')
        
        # 4. Validate Result
        if len(decrypted_seed) == 64:
            print("\n✅ SUCCESS! Decryption successful.")
            print(f"Decrypted Seed: {decrypted_seed}")
            
            # Save strictly for our reference (The final app will do this automatically)
            with open("decrypted_seed_test.txt", "w") as f:
                f.write(decrypted_seed)
        else:
            print("\n❌ Error: Decrypted data is not a 64-character hex string.")
            print(f"Got: {decrypted_seed}")
            
    except ValueError:
        print("\n❌ FAILED to decrypt. The private key does not match the encrypted seed.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    decrypt_test()