import paho.mqtt.client as mqtt
import threading
import time
from collections import defaultdict
import socket
import queue
import json




BROKER_IP = "10.141.41.70"   # HUB IP
DEVICE_NAME = "laptop1"
INBOX_TOPIC = f"{DEVICE_NAME}/inbox"
PACKET_TYPES = ["A", "B", "C"]
packet_counts = defaultdict(int)
dropped_counts = defaultdict(int)
counts_lock = threading.Lock()


# Queue for sending counts to processing thread
stats_queue = queue.Queue()
stats_list=[]
latest_allocated_bw = {
    "HIGH": 0.0,
    "NEUTRAL": 0.0,
    "LOW": 0.0
}



manual_overrides = (None, None) #("Priority, Bandwidth in bps")
class AdaptiveRateChanger:
   def __init__(self, max_rate=10000, packet_size_bytes=1024):
       self.max_rate = max_rate
       self.packet_size_bytes = packet_size_bytes
       self.rates = {
           'HIGH': max_rate / 3,      # packets per second
           'NEUTRAL': max_rate / 3,   # packets per second
           'LOW': max_rate / 3        # packets per second
       }
       self.manual_override = {
           'HIGH': None,
           'NEUTRAL': None,
           'LOW': None
       }
       self.last_send_time = defaultdict(float)
       self.lock = threading.Lock()


   def set_rate_from_bandwidth(self, priority, bandwidth_mbps):
       """
       Set packet rate based on ML-predicted bandwidth
      
       bandwidth_mbps: Target bandwidth in Mbps from ML model
       """
       with self.lock:
           if bandwidth_mbps <= 0:
               self.rates[priority] = 5  # Minimum rate
           else:
               # Convert Mbps to packets per second
               bits_per_second = bandwidth_mbps * 1000000
               bits_per_packet = self.packet_size_bytes * 8
               packets_per_second = bits_per_second / bits_per_packet
              
               # Clamp to reasonable range
               self.rates[priority] = max(10, min(self.max_rate, int(packets_per_second)))
          
           print(f"[{DEVICE_NAME}] Set {priority} rate: {self.rates[priority]} pps ({bandwidth_mbps:.2f} Mbps)")


   def adjust_rate(self, priority, factor):
       """Adjust rate by multiplication factor (e.g., 0.8 to reduce, 1.2 to increase)"""
       with self.lock:
           self.rates[priority] = max(10, min(self.max_rate, int(self.rates[priority] * factor)))
           print(f"[{DEVICE_NAME}] Adjusted {priority} rate to {self.rates[priority]} pps")
  
   def get_delay(self, priority):
       """Get delay between packets in seconds"""
       with self.lock:
           return 1.0 / self.rates[priority]
  
   def get_rate(self, priority):
       """Get current rate for a priority"""
       with self.lock:
           return self.rates[priority]
  
   def check_and_update(self, priority):
       """
       Check if enough time has passed to send/forward a packet.
       Returns True if packet should be forwarded, False if should be dropped.
       """
       with self.lock:
           current_time = time.time()
           delay = 1.0 / self.rates[priority]  # Calculate delay inside lock
           time_since_last = current_time - self.last_send_time[priority]
          
           if time_since_last >= delay:
               self.last_send_time[priority] = current_time
               return True
           return False








# -----------------------------
# MQTT CALLBACKS
# -----------------------------
def on_connect(client, userdata, flags, rc):
   print(f"[{DEVICE_NAME}] Connected with result code {rc}")
   client.subscribe(INBOX_TOPIC)
   print(f"[{DEVICE_NAME}] Subscribed to: {INBOX_TOPIC}")


feedback_data = {
   'laptop2': {'bandwidth': 0.0, 'latency': 0.0, 'priority': 'HIGH'},     # laptop2 handles A,B (HIGH/NEUTRAL)
   'laptop3': {'bandwidth': 0.0, 'latency': 0.0, 'priority': 'NEUTRAL'},  # laptop3 handles C (LOW)
}
feedback_lock = threading.Lock()


DEVICE_TO_PRIORITY = {
   'laptop2': 'HIGH',      # laptop2 gets A and B, treat as HIGH
   'laptop3': 'NEUTRAL',   # laptop3 gets C, treat as NEUTRAL
}


def on_message(client, userdata, msg):
   message = msg.payload.decode()
   print(f"\n[{DEVICE_NAME}] Received on {msg.topic}: {message}")


   if message[1] == "M" or message[1] == "L":
       try:
           # Extract device from topic (e.g., "laptop2/inbox" -> "laptop2")
           device = message[0]
          
           if message[1] == "M":
               # Bandwidth message: M123.45 means 123.45 Mbps
               x = message[0:1]
               bandwidth = float(message[2:])
               with feedback_lock:
                   if f'laptop{device}' in feedback_data:
                       feedback_data[f'laptop{device}']['bandwidth'] = bandwidth
                       print(f"[{DEVICE_NAME}] 📊 {device} Bandwidth: {bandwidth:.2f} Mbps")
           elif message[1] == "L":
               # Latency message: L45.67 means 45.67 ms
               x = message[0:1]
               latency = float(message[2:])
               with feedback_lock:
                   if f'laptop{device}' in feedback_data:
                       feedback_data[f'laptop{device}']['latency'] = latency
                       print(f"[{DEVICE_NAME}] ⏱️  {device} Latency: {latency:.2f} ms")


       except (ValueError, IndexError) as e:
           print(f"[{DEVICE_NAME}] Error parsing feedback '{message}': {e}")
  


# -----------------------------
# SENDER THREAD
# -----------------------------
rate_limiter = AdaptiveRateChanger(max_rate=1000)
last_send_time = {'HIGH': 0,
   'NEUTRAL': 0,
   'LOW': 0
}
def udp_packet_rerouter(client, listen_ip="0.0.0.0", listen_port=5005, buffer_size=65535):
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.bind((listen_ip, listen_port))
   print(f"[{DEVICE_NAME}] UDP Receiver listening on {listen_ip}:{listen_port}")


   TAG_TO_PRIORITY = {
       'A': 'HIGH',
       'B': 'HIGH',
       'C': 'LOW',
   }
   while True:
       data, addr = sock.recvfrom(buffer_size)
       try:
           decoded = data.decode("utf-8", errors="ignore")
           packet = decoded.split(":")
           tag = packet[0].strip()
       except:
           tag = "<decode error>"
      
       with counts_lock:
           packet_counts[tag] += 1
      
       priority = TAG_TO_PRIORITY.get(tag, 'LOW')
       delay = rate_limiter.get_delay(priority)
       if rate_limiter.check_and_update(priority) :
           rerouter(client, tag, decoded, data)
       else:
           # Drop packet due to rate limiting
           
           dropped_counts[tag] += 1
           if dropped_counts[tag] % 100 == 0:  # Log every 100 drops
               print(f"[{DEVICE_NAME}]: Dropped {dropped_counts[tag]} {tag} packets (rate limited)")






def rerouter(client, tag, content, raw_data):
   if(DEVICE_NAME != "laptop1"):
       return  # Only laptop1 reroutes packets


   # Tag to topic mapping
   tag_routing = {
       "A": "laptop2/inbox",
       "B": "laptop2/inbox",
       "C": "laptop3/inbox"
   }
  
   # Get target topic from mapping
   target_topic = tag_routing.get(tag)
   
   if target_topic:
       priority = DEVICE_TO_PRIORITY.get(target_topic.split("/")[0], "LOW")
       with feedback_lock:
           actual_bw = feedback_data[target_topic.split("/")[0]]["bandwidth"]
           allocated_bw = latest_allocated_bw[priority]
       if actual_bw > allocated_bw:
           print(f"[{DEVICE_NAME}] HARD STOP: {priority} actual BW {actual_bw:.2f} > allocated {allocated_bw:.2f}. Packet dropped.")
           return
       client.publish(target_topic, content)
       #print(f"[{DEVICE_NAME}] Rerouted UDP packet to {target_topic} | TYPE: {tag} | Size: {len(raw_data)}")
   else:
       print(f"[{DEVICE_NAME}] Unknown tag '{tag}' - no routing rule")


def stats_collector_thread(interval=5):
   """Periodically collect packet counts and send to processing"""
   while True:
       time.sleep(interval)
      
       # Get snapshot of current counts
       with counts_lock:
           counts_snapshot = {ptype: 0 for ptype in PACKET_TYPES}
           counts_snapshot.update(packet_counts)
           # Optional: reset counts after sending (for delta/incremental counting)
           packet_counts.clear()


       # Send to stats processing
       if counts_snapshot:
           stats_queue.put(counts_snapshot)
           #print(f"[{DEVICE_NAME}] Stats collected: {counts_snapshot}")


def ml_processing_thread(stats_queue, device_name):
    try:
        from ml_brain import LiveBandwidthPredictor
    except ImportError:
        print("[ML Thread] Warning: ml_model.py not found. ML processing disabled.")
        return
    ml_model = LiveBandwidthPredictor(max_total_bandwidth=1000.0)
    training_enabled = True
    accuracy_history = []
    target_accuracy = 70.0  # Target accuracy percentage to stop training
    min_samples = 20        # Minimum samples to consider for accuracy
    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
           
            with counts_lock:
                if not stats_queue.empty():
                    stats = stats_queue.get()
                    stats = list(stats.values())
                    # Extract just the message text
                   
                    # Call your ML model
                    with feedback_lock:
                        actual_bandwidths = {
                            'HIGH': feedback_data['laptop2']['bandwidth'],
                            'NEUTRAL': feedback_data['laptop2']['bandwidth'],
                            'LOW': feedback_data['laptop3']['bandwidth']
                        }
                       
                       
                        latencies = {
                            'HIGH': feedback_data['laptop2']['latency'],
                            'NEUTRAL': feedback_data['laptop2']['latency'],
                            'LOW': feedback_data['laptop3']['latency']
                        }


                    pred = ml_model.predict(stats)


                    if(manual_overrides[0] is not None and manual_overrides[1] is not None):
                        priority, bandwidth = manual_overrides
                        actual_bandwidths[priority] = bandwidth
                  
                  
                    if training_enabled:
                        train_predictions, errors = ml_model.train_with_feedback(
                            stats,
                            actual_bandwidths,
                            latencies
                        )
                      
                        # Calculate accuracy
                        mae_high = abs(errors[0])
                        mae_neutral = abs(errors[1])
                        mae_low = abs(errors[2])
                      
                        mape_high = (mae_high / max(actual_bandwidths['HIGH'], 0.01)) * 100
                        mape_neutral = (mae_neutral / max(actual_bandwidths['NEUTRAL'], 0.01)) * 100
                        mape_low = (mae_low / max(actual_bandwidths['LOW'], 0.01)) * 100
                      
                        accuracy_high = min(max(0, 100 - mape_high), 100)
                        accuracy_neutral = min(max(0, 100 - mape_neutral), 100)
                        accuracy_low = min(max(0, 100 - mape_low), 100)
                        accuracy_avg = min((accuracy_high + accuracy_neutral + accuracy_low) / 3, 100)
                      
                        # Track accuracy
                        accuracy_history.append(accuracy_avg)
                        if len(accuracy_history) > 10:
                            accuracy_history.pop(0)
                      
                        if len(accuracy_history) >= min_samples:
                            recent_avg = sum(accuracy_history[-min_samples:]) / min_samples
                            if recent_avg >= target_accuracy:
                                training_enabled = False
                                print(f"🎉 Target accuracy reached! Training stopped.")


                    # Update rate limiter based on predictions
                    rate_limiter.set_rate_from_bandwidth('HIGH', pred['HIGH'])
                    rate_limiter.set_rate_from_bandwidth('NEUTRAL', pred['NEUTRAL'])
                    rate_limiter.set_rate_from_bandwidth('LOW', pred['LOW'])
                    data_history = []
                    MAX_HISTORY = 60
                    # In ml_processing_thread(), replace the dashboard_data section with:
                    dashboard_data = {
                        "A": {"allocated": pred['HIGH'] * 10, "usage": actual_bandwidths['HIGH']},
                        "B": {"allocated": pred['NEUTRAL'] * 10, "usage": actual_bandwidths['NEUTRAL']},
                        "C": {"allocated": pred['LOW'] * 10, "usage": actual_bandwidths['LOW']},
                        "ACC": {"accuracy": accuracy_avg}
                    }

                    latest_allocated_bw["HIGH"] = pred["HIGH"]
                    latest_allocated_bw["NEUTRAL"] = pred["NEUTRAL"]
                    latest_allocated_bw["LOW"] = pred["LOW"]

                    # Save to history
                    data_history.append(dashboard_data)
                    if len(data_history) > MAX_HISTORY:
                        data_history.pop(0)

                    # Write both current and history
                    with open("dashboard_data.json", "w") as f:
                        json.dump({"current": dashboard_data, "history": data_history}, f)

                                      
                    result = f"Predicted Bandwidths: HIGH={pred['HIGH']} Mbps, NEUTRAL={pred['NEUTRAL']} Mbps, LOW={pred['LOW']} Mbps"
                    print(f"[ML Thread] ML Model Result: {result}\n")
        except Exception as e:
            print(f"[ML Thread] Error: {e}")


# -----------------------------
# MAIN PROGRAM
# -----------------------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


print(f"[{DEVICE_NAME}] Connecting to broker at {BROKER_IP}...")
client.connect(BROKER_IP, 1883, 60)


# Run MQTT loop in a background thread
#threading.Thread(target=client.loop_forever, daemon=True).start()


#Start MQTT loop thread
threading.Thread(target=client.loop_forever, daemon=True).start()
# Start UDP packet rerouter thread
threading.Thread(target=udp_packet_rerouter, args=(client,), daemon=True).start()
# Start stats collector thread
threading.Thread(target=stats_collector_thread, daemon=True).start()
#ML Processing thread
threading.Thread(target=ml_processing_thread, args=(stats_queue, DEVICE_NAME), daemon=True).start()


try:
   while True:
       time.sleep(1)
except KeyboardInterrupt:
   print(f"\n[{DEVICE_NAME}] Exiting program...")