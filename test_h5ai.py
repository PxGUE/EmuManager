import requests

url = "https://buildbot.libretro.com/_h5ai/public/server/php/index.php"
payload = {
    "action": "get",
    "items": "true",
    "items_href": "/nightly/windows/x86_64/latest/",
    "items_what": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json" # h5ai sometimes expects JSON POST
}

# h5ai expects a JSON body for some actions
import json
try:
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")
