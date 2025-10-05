import time

import requests

url = "http://localhost:8808/prompts"
data = {"query": "What is the biggest challenge in space biology currently?"}
headers = {"X-Lunbi-Token": "8e1c6b5f4a7d49e9b2a3c8f9d6712f4a"}

s = time.perf_counter()
response = requests.post(url, headers=headers, json=data)
response.raise_for_status()
print(response.json())
e = time.perf_counter()
print(f"Time: {e-s:.2f}s")