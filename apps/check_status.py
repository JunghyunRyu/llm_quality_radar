#!/usr/bin/env python3
import requests
import time

test_id = "web_test_20250807_005234"

for i in range(10):
    try:
        response = requests.get(f"http://localhost:8000/report/{test_id}")
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            current_step = result.get("current_step", "Unknown")
            progress = result.get("progress", 0)
            print(
                f"Check {i+1}: Status={status}, Step={current_step}, Progress={progress}%"
            )
        else:
            print(f"Check {i+1}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Check {i+1}: Error - {e}")

    time.sleep(1)
