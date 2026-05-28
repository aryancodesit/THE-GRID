$path = "d:\PICOCTF\EASY\Corrupted File\Corrupted File"
$bytes = [System.IO.File]::ReadAllBytes($path)
Write-Host "Current Header:"
$bytes[0..9] | ForEach-Object { Write-Host -NoNewline ("{0:X2} " -f $_) }
