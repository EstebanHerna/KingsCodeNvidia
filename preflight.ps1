$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"
py tools\preflight.py
py tools\inspect_challenge.py
