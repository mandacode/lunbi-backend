import requests

chunk_size = 8192 * 1000 * 1000
url = "http://localhost:8808/prompts/stream"
data = {"query": "What are current NASA priorities in space biology?"}
headers = {"X-Lunbi-Token": "8e1c6b5f4a7d49e9b2a3c8f9d6712f4a"}

with requests.post(url, headers=headers, json=data, stream=True) as response:
    response.raise_for_status()
    for chunk in response.iter_lines():
        print(chunk)

