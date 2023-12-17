from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os


def aes_256_encrypt(key, plaintext):
    # Generate a random IV (Initialization Vector)
    iv = os.urandom(16)

    # Pad the plaintext
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    # Create an AES-256 cipher with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the padded data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Return the IV and ciphertext
    return iv + ciphertext


def aes_256_decrypt(key, ciphertext):
    # Extract the IV from the ciphertext
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]

    # Create an AES-256 cipher with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad the data
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    # Return the decrypted plaintext
    return plaintext
