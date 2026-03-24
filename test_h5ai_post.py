import requests
import json

url = "https://buildbot.libretro.com/nightly/windows/x86_64/latest/"
payload = {
    "action": "get",
    "custom": "/nightly/windows/x86_64/latest/"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": url
}

try:
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        entries = data.get("entries", [])
        print(f"Found {len(entries)} entries.")
        for e in entries[:5]:
            print(f" - {e.get('abs_href')}")
    else:
        print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")
