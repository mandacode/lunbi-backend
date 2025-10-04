import time

import requests

url = "http://localhost:8808/prompts/stream"
data = {"query": "What are current NASA priorities in space biology?"}
headers = {"X-Lunbi-Token": "8e1c6b5f4a7d49e9b2a3c8f9d6712f4a"}

s = time.perf_counter()
with requests.post(url, headers=headers, json=data, stream=True) as response:
    response.raise_for_status()
    e1 = time.perf_counter()
    for chunk in response.iter_lines():
        print(chunk.decode("utf-8"), end="")

e = time.perf_counter()
print(f"First response: {e1-s:.2f}s")
print(f"Time: {e-s:.2f}s")