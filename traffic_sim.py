import requests
import time

# The target node to attack (Worker 1 on Port 5001)
TARGET_URL = "http://127.0.0.1:5001/trigger_spike"

def start_simulation():
    print("--- TRAFFIC SIMULATOR ---")
    print("1. Waiting for system to stabilize...")
    
    # Countdown to build suspense
    for i in range(5, 0, -1):
        print(f"   Starting heavy load in {i}...")
        time.sleep(1)
    
    print("\n💥 INJECTING HEAVY TRAFFIC into Worker_1...")
    try:
        # Send the POST request to the server to increase its internal counter
        response = requests.post(TARGET_URL)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server Response: {data['message']}")
            print(f"   📈 New Load on Server: {data['new_load']} Mbps")
            print("\nNow watch the AI Agent terminal to see it detect this spike!")
        else:
            print(f"   ❌ Server returned error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to connect. Is node_server.py running on port 5001?")
        print(f"   Error: {e}")

if __name__ == "__main__":
    start_simulation()