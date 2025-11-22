from flask import Flask, jsonify, request
import random
import os
import sys

app = Flask(__name__)

# Default to port 5000 if not specified
PORT = 5000
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

NODE_NAME = f"Local_Node_{PORT}"

# State
current_traffic = 100

@app.route('/')
def home():
    return f"Node {NODE_NAME} is active on port {PORT}."

@app.route('/get_stats', methods=['GET'])
def get_stats():
    global current_traffic
    
    # 1. Natural Fluctuation (The "Noise")
    # Traffic wiggles between -10 and +20 mbps normally
    change = random.randint(-10, 20)
    current_traffic += change
    
    # Prevent it from going below zero or exploding without cause
    if current_traffic < 50: current_traffic = 50
    if current_traffic > 150 and current_traffic < 200: current_traffic = 140 # dampening
    
    return jsonify({
        "node": NODE_NAME,
        "traffic_mbps": current_traffic,
        "status": "ok"
    })

@app.route('/trigger_spike', methods=['POST'])
def trigger_spike():
    """This simulates a sudden surge (e.g. 4K Video Stream started)"""
    global current_traffic
    surge_amount = 400
    current_traffic += surge_amount
    print(f"⚠️ [SIMULATION] TRAFFIC SPIKE INJECTED! Load is now {current_traffic} Mbps")
    return jsonify({"message": "SPIKE_INJECTED", "new_load": current_traffic})

if __name__ == '__main__':
    print(f"Starting {NODE_NAME} on Port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)