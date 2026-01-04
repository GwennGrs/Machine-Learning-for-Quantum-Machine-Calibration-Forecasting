import requests
import time
import json
import os
from datetime import datetime, timezone

## Dashboard ID Tuna9
dashboard_id = "c9fd5bfb9dc5421e8b9e845369f61a97"
panel_ids = range(2, 21, 2)
headers = {
    "Content-Type": "application/json",
    "X-Grafana-Org-Id": "1"
}

interval_ms = 20000
max_points = 1000
now = int(time.time() * 1000)
all_panels_data = {}

for pid in panel_ids:    
    url = f"https://monitoring.qutech.support/api/public/dashboards/{dashboard_id}/panels/{pid}/query"
    
    payload = {
        "intervalMs": interval_ms,
        "maxDataPoints": max_points,
        "timeRange": {
            "from": str(now),
            "to": str(now),
            "timezone": "browser"
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        all_panels_data[f"panel_{pid}"] = response.json()
        print("Extracted", pid)
    else:
        print("Error", pid)

os.makedirs("data_panels", exist_ok=True)
with open("data_panels/tuna9.json", "w") as f:
    json.dump(all_panels_data, f, indent=2)