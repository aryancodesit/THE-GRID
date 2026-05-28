
import re

log_path = r"C:\Users\aryan\.gemini\antigravity\scratch\log_utf8.txt"

def get_flag():
    flag_parts = []
    seen = set()
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "FLAGPART" in line:
                part = line.split("FLAGPART:")[1].strip()
                if part not in seen:
                    flag_parts.append(part)
                    seen.add(part)
    
    print("".join(flag_parts))

if __name__ == "__main__":
    get_flag()
