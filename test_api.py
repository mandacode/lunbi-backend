import requests

def test_api():
    url = "http://localhost:8808/prompt"
    query = "What are current NASA priorities in space biology?"
    data = {"query": query}
    response = requests.post(url, json=data)
    print(response.json())



if __name__ == "__main__":
    test_api()
