import requests
import time

TARGET_URL = "http://127.0.0.1:5001/trigger_spike"

def start_simulation():
    print("--- 6G TRAFFIC SIMULATOR (Full Lifecycle) ---")
    
    # 1. Trigger Static Upgrade (Medical)
    print("\n1. 🚑 SIMULATING EMERGENCY (Static Level Test)...")
    print("   Sending 'MEDICAL' VIP Tag...")
    try:
        payload = {"type": "MEDICAL"}
        requests.post(TARGET_URL, json=payload)
        print(f"   ✅ VIP Tag Sent.")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print("   (Waiting 6 seconds for system to stabilize/downgrade...)")
    time.sleep(6) 
    
    # 2. Trigger Dynamic Upgrade (High Lag)
    print("\n2. 🐢 SIMULATING HIGH LAG (Dynamic Level Test)...")
    print("   Sending 'NORMAL' packet with Heavy Load...")
    try:
        # Normal tag, but adds load to trigger latency check
        requests.post(TARGET_URL, json={"type": "NORMAL"}) 
        print("   ✅ Heavy Load Injected.")
        print("   -> Watch AI for: 'HIGH_LATENCY_DETECTED'")
    except:
        print("   ❌ Connect failed.")

if __name__ == "__main__":
    start_simulation()