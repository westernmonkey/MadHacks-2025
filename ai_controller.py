import requests
import time

# --- CONFIG ---
NODES = [
    {"name": "Worker_1", "url": "http://127.0.0.1:5001"},
    # Add your other nodes here if needed
]

# TARGETS
LATENCY_TARGET = 50 # The Soft Spot Ceiling (50ms)

# STATE TRACKING
# Tracks how long a node has been "Good" so we can downgrade it
cool_down_tracker = {} 

def get_node_stats(node):
    try:
        response = requests.get(f"{node['url']}/get_stats", timeout=1)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def analyze_node(node_name, stats):
    current_load = stats['traffic_mbps']
    packet_type = stats['packet_type']
    current_latency = stats['latency_ms']
    
    # Initialize tracker if new
    if node_name not in cool_down_tracker:
        cool_down_tracker[node_name] = 0

    print(f"   📊 {node_name}: Type=[{packet_type}] | Latency={current_latency}ms | Load={current_load}")
    
    # --- LAYER 1: STATIC CHECK (Identity - The VIP Pass) ---
    if packet_type == "MEDICAL":
        cool_down_tracker[node_name] = 0 # Reset cool down timer
        print(f"      🚑 CRITICAL TAG DETECTED: {packet_type}")
        return True, "FORCE_GOLD_SLICE_VIP"

    # --- LAYER 2: DYNAMIC CHECK (The Performance Hunt) ---
    if current_latency > LATENCY_TARGET:
        cool_down_tracker[node_name] = 0 # Reset cool down timer
        return True, f"HIGH_LATENCY_DETECTED ({current_latency}ms)"
        
    # --- LAYER 3: THE DOWNGRADE (The Clean Up) ---
    # If we get here, traffic is Normal AND Latency is Low.
    # We start counting...
    cool_down_tracker[node_name] += 1
    
    if cool_down_tracker[node_name] >= 3:
        # If we have been stable for 3 cycles (~5 seconds), release the resources.
        print("      📉 Network is Stable. Releasing Resources.")
        return False, "DOWNGRADE_TO_SILVER"
        
    elif current_latency < 10:
        print("      ⚡ System is over-performing. Saving Power.")
        return False, "OPTIMIZING_POWER"
        
    else:
        print("      ✅ Soft Spot Found. Holding Steady.")
        return False, "SOFT_SPOT"

def run_simulation():
    print("\n🤖 6G AGENT (Layers: Static + Dynamic + Downgrade)")
    print("-" * 50)

    while True:
        for node in NODES:
            stats = get_node_stats(node)
            if stats:
                needs_upgrade, reason = analyze_node(node['name'], stats)
                
                if needs_upgrade:
                    print(f"      🚨 ACTION: {reason}")
                    print(f"      🚀 Allocating GOLD SLICE to {node['name']}\n")
                
                elif reason == "DOWNGRADE_TO_SILVER":
                    print(f"      ♻️ ACTION: Downgrading {node['name']} to SILVER SLICE (Save Energy)\n")
                    # Reset counter so we don't spam downgrade messages
                    cool_down_tracker[node['name']] = 0
                
                else:
                    pass
        
        time.sleep(1.5)

if __name__ == "__main__":
    run_simulation()