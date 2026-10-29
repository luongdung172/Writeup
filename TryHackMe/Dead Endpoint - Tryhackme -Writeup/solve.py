
from pathlib import Path
from datetime import datetime, timezone
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import sys

MASK = (1 << 64) - 1

# Reconstructed from IDA: sub_1509()
def sub_1509(state):
    state = (state - 0x61C8864680B583EB) & MASK

    z = ((state ^ (state >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    z = z ^ (z >> 31)

    return state, z


# Reconstructed from main(): generate 32-byte AES key
def generate_key(seed):
    state = seed
    key = bytearray()

    for _ in range(4):
        state, value = sub_1509(state)
        key.extend(value.to_bytes(8, "little"))

    return bytes(key)


# Extract GCM parameters from encrypted file
data = Path(sys.argv[1]).read_bytes()

assert data[:4] == b"GPH1"

aad = data[:28]
nonce = data[16:28]
tag = data[28:44]
ciphertext = data[48:]


# Brute-force candidate timestamps (milliseconds)
start = 1792474614561
end = 1792474614752

for seed in range(start, end + 1):
    key = generate_key(seed)

    try:
        plaintext = AESGCM(key).decrypt(
            nonce,
            ciphertext + tag,
            aad
        )

        print("[+] FOUND INITIAL SEED:", seed)
        print("[+] AES-256 KEY:", key.hex())
        print("[+] UTC:", datetime.fromtimestamp(
            seed / 1000, tz=timezone.utc
        ))
        print("[+] GCM authentication: VALID")
        print("[+] JPEG header:", plaintext[:4].hex())
        out = Path("recovered")
        out.mkdir(exist_ok=True)

        filename = Path(sys.argv[1]).name.removesuffix(".locked")
        output = out / filename

        with output.open("xb") as f:
            f.write(plaintext)

        print("[+] Decrypted image saved:", output)
        break

    except InvalidTag:
        continue
else:
    print("[-] No matching seed found")
