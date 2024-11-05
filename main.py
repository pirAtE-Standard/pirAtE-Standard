from flask import Flask, request, jsonify, abort
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
import base64

import wordset

app = Flask(__name__)

# Standard IV to use (this way the IV does not need to be known in addition to password)
iv = b"0000000000000000"

# POST request for encryption
@app.route("/get-piratified-text/", methods=["POST"])
def get_encrypted_text():
    # Grab JSON and args
    try:
        data = request.get_json()
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
    
    plain_text = data.get("plaintext")
    key = data.get("key")

    # Validate data is not null
    if plain_text is None or key is None:
        return jsonify({'error': 'Missing JSON data'}), 400

    return __pirAtES__(plain_text, key)

# Function that does the encryption/pirate substitution
def __pirAtES__(plain_text, key):
    # Encode args so they play well with C
    byte_plain_text = plain_text.encode("utf-8")
    byte_key = key.encode("utf-8")
    
    # Create cipher
    cipher = AES.new(byte_key, AES.MODE_CBC, iv)

    # Encrypt the text
    cipher_text = cipher.encrypt(pad(byte_plain_text, AES.block_size))
    
    # Make sure to decode to base256 so it translates well when copied
    return jsonify(base64.b64encode(cipher_text).decode("utf-8"), 200)

# POST request for decryption
@app.route("/get-plain-text/", methods=["POST"])
def get_decrypted_text():
    # Grab JSON and args
    try:
        data = request.json
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400

    cipher_text = data.get("ciphertext")
    key = data.get("key")

    # Validate data is not null
    if cipher_text is None or key is None:
        return jsonify({'error': 'Missing JSON data'}), 400

    return __undo_pirAtES__(cipher_text, key)

# Function that undoes pirate substitution/decrypts
def __undo_pirAtES__(cipher_text, key):
    # Encode args so they play well with C
    byte_cipher_text = base64.b64decode(cipher_text)
    byte_key = key.encode("utf-8")

    # Create cipher
    cipher = AES.new(byte_key, AES.MODE_CBC, iv)

    # Decrypt the text
    plain_text = unpad(cipher.decrypt(byte_cipher_text), AES.block_size)

    return jsonify(plain_text.decode("utf-8"), 200)


if __name__ == "__main__":
    app.run(debug=True)