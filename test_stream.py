import requests
chunk_size = 8192 * 1000 * 1000
url = "http://localhost:8808/prompts/stream"
data = {"query": "What are current NASA priorities in space biology?"}
with requests.post(url, json=data, stream=True) as response:
    response.raise_for_status()
    for chunk in response.iter_lines():
        print(chunk)

