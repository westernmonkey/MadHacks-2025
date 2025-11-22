import requests
import time

# --- LOCAL SIMULATION CONFIG ---
NODES = [
    {"name": "Worker_1", "url": "http://127.0.0.1:5001"},
    {"name": "Worker_2", "url": "http://127.0.0.1:5002"},
]

# Thresholds
BANDWIDTH_LIMIT = 300  # If traffic > 300, we need an upgrade
UPGRADE_LIMIT = 1000   # The new 6G slice capacity

# Memory for Moving Average
history = {}

def get_node_stats(node):
    try:
        response = requests.get(f"{node['url']}/get_stats", timeout=1)
        if response.status_code == 200:
            return response.json()['traffic_mbps']
    except:
        return 0
    return 0

def analyze_traffic(node_name, current_load):
    # Initialize history
    if node_name not in history:
        history[node_name] = []
    
    # Keep last 5 readings
    history[node_name].append(current_load)
    if len(history[node_name]) > 5: history[node_name].pop(0)
    
    # AI LOGIC: Simple Trend Prediction
    if len(history[node_name]) >= 2:
        # Calculate slope (rate of change)
        # If load went 100 -> 150, growth is 50.
        growth = history[node_name][-1] - history[node_name][0]
        
        # Predict next step
        prediction = current_load + growth
        
        print(f"   📊 {node_name}: Load={current_load} Mbps | Trend={growth:+d} | Pred={prediction}")
        
        if prediction > BANDWIDTH_LIMIT:
            return True
            
    return False

def run_simulation():
    print("\n🤖 6G NETWORK SLICING AGENT (Local Simulation)")
    print(f"   Monitoring {len(NODES)} Local Nodes...")
    print(f"   Threshold: {BANDWIDTH_LIMIT} Mbps")
    print("-" * 50)

    while True:
        for node in NODES:
            load = get_node_stats(node)
            needs_upgrade = analyze_traffic(node['name'], load)
            
            if needs_upgrade:
                print(f"   🚨 PREDICTION ALERT: {node['name']} will exceed capacity!")
                print(f"   🚀 AUTOMATED ACTION: Switching {node['name']} to GOLD SLICE ({UPGRADE_LIMIT} Mbps)")
                print("   ✅ Resource Re-allocation Complete.\n")
            else:
                # Optional: Print nothing if healthy to keep screen clean
                pass
                
        time.sleep(1.5) # Scan every 1.5 seconds

if __name__ == "__main__":
    run_simulation()