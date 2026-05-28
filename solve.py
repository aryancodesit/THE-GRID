import re

file_path = r"d:\PICOCTF\Playlist\The Beginner's Guide to the picoGym\strings"

try:
    with open(file_path, "rb") as f:
        data = f.read()
        # Find sequences of at least 4 printable characters
        strings = re.findall(b"[ -~]{4,}", data)
        for s in strings:
            try:
                decoded = s.decode("utf-8")
                if "picoCTF" in decoded:
                    with open("final_flag.txt", "w") as out:
                        out.write(decoded)
                    print("Flag written to final_flag.txt")
            except:
                pass
except Exception as e:
    print(f"Error: {e}")
