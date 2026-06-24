import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:5000/submit"
payload = {
    "text": "This is a test submission for rate limit testing purposes only and nothing else.",
    "creator_id": "ratelimit-test"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}
)

try:
    response = urllib.request.urlopen(req)
    print("200 OK")
except urllib.error.HTTPError as e:
    print(f"{e.code} BLOCKED")
except Exception as e:
    print(f"Error: {e}")