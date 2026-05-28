import os

content = b"\x00\x01\x02" * 100 + b"some_garbage_picoCTF{t3st_fl4g}_more_garbage" + b"\xff" * 100
with open("dummy.bin", "wb") as f:
    f.write(content)
