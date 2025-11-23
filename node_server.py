from flask import Flask, jsonify, request
import random
import os
import sys

app = Flask(__name__)

# Default Port 5001
PORT = 5001
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

NODE_NAME = f"Local_Node_{PORT}"

# --- STATE VARIABLES ---
# Start LOW (30 Mbps) so Latency is ~15ms. 
# This ensures the AI stays quiet (No "False Alarms") when idle.
current_traffic = 30 
last_packet_type = "NORMAL"

@app.route('/')
def home():
    return f"Node {NODE_NAME} is active."

@app.route('/get_stats', methods=['GET'])
def get_stats():
    global current_traffic
    
    # 1. AGGRESSIVE AUTO-DECAY (The "Downgrade Enabler")
    # If traffic is high (from a previous spike), drain it FAST.
    # This forces the latency down, allowing the AI to see "Stability" and trigger the Downgrade.
    if current_traffic > 50:
        current_traffic -= 50 # Drop 50 Mbps every time the AI checks
    else:
        # 2. GENTLE IDLE
        # Only wiggle slightly if we are already low.
        change = random.randint(-2, 2) 
        current_traffic += change
    
    # 3. SAFETY CLAMP (Prevent Negative Numbers)
    if current_traffic < 30: current_traffic = 30
    
    # 4. CALCULATE LATENCY
    # Logic: Latency = Traffic / 2. 
    # Idle (30 Mbps) -> 15ms (Perfect - No Alerts).
    # Spiked (300 Mbps) -> 150ms (High Latency Alert).
    current_latency = int(current_traffic / 2) + random.randint(-1, 1)
    
    return jsonify({
        "node": NODE_NAME,
        "traffic_mbps": current_traffic,
        "latency_ms": current_latency, 
        "packet_type": last_packet_type,
        "status": "ok"
    })

@app.route('/trigger_spike', methods=['POST'])
def trigger_spike():
    global current_traffic, last_packet_type
    
    data = request.json or {}
    packet_type = data.get("type", "NORMAL") 
    last_packet_type = packet_type 
    
    # Add massive traffic to ensure we definitely cross the 50ms threshold
    current_traffic += 400
    
    print(f"⚠️ RECEIVED PACKET: Type={packet_type} | Load={current_traffic}")
    return jsonify({"message": "PACKET_RECEIVED", "type": packet_type})

if __name__ == "__main__":
    print(f"Starting {NODE_NAME} on Port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)