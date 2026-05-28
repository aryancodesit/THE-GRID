$path = "d:\PICOCTF\EASY\Corrupted File\Corrupted File"

# Read all bytes
$bytes = [System.IO.File]::ReadAllBytes($path)

# Print first 16 bytes for inspection
Write-Host "Original Header Bytes:"
$bytes[0..15] | ForEach-Object { Write-Host -NoNewline ("{0:X2} " -f $_) }
Write-Host ""

# JPEG Magic Bytes: FF D8 FF E0 (JFIF)
# Let's fix the first 4 bytes
$bytes[0] = 0xFF
$bytes[1] = 0xD8
$bytes[2] = 0xFF
$bytes[3] = 0xE0

# Write back to file
[System.IO.File]::WriteAllBytes($path, $bytes)

Write-Host "Repaired Header Bytes:"
$bytes[0..15] | ForEach-Object { Write-Host -NoNewline ("{0:X2} " -f $_) }
Write-Host ""
Write-Host "File repaired successfully."
