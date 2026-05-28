import gzip
import re
import os

gz_path = r"d:\PICOCTF\EASY\DISKO 1\DISKO 1.gz"
img_path = r"d:\PICOCTF\EASY\DISKO 1\disk.img"

# 1. Decompress
print(f"Decompressing {gz_path}...")
try:
    with gzip.open(gz_path, 'rb') as f_in:
        with open(img_path, 'wb') as f_out:
            f_out.write(f_in.read())
    print(f"Decompressed to {img_path}")
except Exception as e:
    print(f"Error decompressing: {e}")
    exit(1)

# 2. Search for Flag
print("Searching for flag in disk image...")
try:
    with open(img_path, 'rb') as f:
        content = f.read()
        # Look for the flag format picoCTF{...}
        matches = re.findall(b'picoCTF\{[^}]+\}', content)
        for match in matches:
            print(f"FOUND FLAG: {match.decode('utf-8', errors='ignore')}")
            
        if not matches:
            print("Flag not found with regex. Trying 'strings' approach...")
            # Simple strings implementation: sequences of 4+ printable chars
            chars = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ "
            regexp = b'[%s]{4,}' % re.escape(chars)
            all_strings = re.findall(regexp, content)
            for s in all_strings:
                if b'pico' in s:
                    print(f"Possible match: {s.decode()}")

except Exception as e:
    print(f"Error searching: {e}")
