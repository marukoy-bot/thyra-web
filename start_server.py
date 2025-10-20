import subprocess
import sys
import os
import webbrowser
import time
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Use a non-routable IP to trigger local IP resolution
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

local_ip = get_local_ip()
server_url = f"http://{local_ip}:8000"
print(f"Launching server at {server_url}")

# Launch FastAPI server
process = subprocess.Popen(
    ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

browser_opened = False

for line in process.stdout:
    print(line, end="")
    if not browser_opened and "Application startup complete" in line:
        webbrowser.open(server_url)
        browser_opened = True
