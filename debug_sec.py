import requests

# Use your real ASU email here
headers = {"User-Agent": "EquityAnalystPortfolio/1.0 (mcastr76@asu.edu)"}

# MU's actual SEC CIK is 0000720858. Let's bypass the lookup and hit the submissions URL directly.
url = "https://data.sec.gov/submissions/CIK0000720858.json"

print(f"🔍 Requesting data from SEC...")
response = requests.get(url, headers=headers)

print(f"📡 Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Success! The top-level keys in this JSON are: {list(data.keys())}")
    
    # Let's check where 'recent' actually lives
    if 'recent' in data:
        print("🎯 Found 'recent' at the TOP LEVEL!")
    elif 'filings' in data and 'recent' in data['filings']:
        print("🎯 Found 'recent' NESTED inside the 'filings' key!")
    else:
        print("❌ 'recent' is missing entirely. Here is a sample of the data:")
        print(str(data)[:500])
else:
    print(f"❌ The SEC blocked us or the file doesn't exist. Raw response: {response.text[:500]}")