import paho.mqtt.client as mqtt
import threading
import time
import os
from collections import defaultdict
import socket
import queue


BROKER_IP = "10.141.41.70"   # HUB IP
DEVICE_NAME = ""             # laptop1, laptop2, laptop3

PACKET_TYPES = ["A", "B", "C"]
packet_counts = defaultdict(int)
dropped_counts = defaultdict(int)
counts_lock = threading.Lock()

# Queue for sending counts to processing thread
stats_queue = queue.Queue()
stats_list=[]

class AdaptiveRateChanger:
    def __init__(self, max_rate=10000, packet_size_bytes=1024):
        self.max_rate = max_rate
        self.packet_size_bytes = packet_size_bytes
        self.rates = {
            'HIGH': max_rate / 3,      # packets per second
            'NEUTRAL': max_rate / 3,   # packets per second
            'LOW': max_rate / 3        # packets per second
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
                bits_per_second = bandwidth_mbps * 1_000_000
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
# ASK USER WHICH DEVICE THIS IS
# -----------------------------
while DEVICE_NAME not in ["laptop1", "laptop2", "laptop3"]:
    DEVICE_NAME = input("Enter device name (laptop1 / laptop2 / laptop3): ").strip()

INBOX_TOPIC = f"{DEVICE_NAME}/inbox"
OUTBOX_TOPIC = "laptop1/inbox"   # All laptops send to HUB
SAVE_FILE = f"{DEVICE_NAME}_messages.txt"


# -----------------------------
# MQTT CALLBACKS
# -----------------------------
def on_connect(client, userdata, flags, rc):
    print(f"[{DEVICE_NAME}] Connected with result code {rc}")
    client.subscribe(INBOX_TOPIC)
    print(f"[{DEVICE_NAME}] Subscribed to: {INBOX_TOPIC}")


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"\n[{DEVICE_NAME}] Received on {msg.topic}: {message}")

    # Save message to a file
    #with open(SAVE_FILE, "a") as f:
     #   f.write(f"{time.ctime()} - {msg.topic}: {message}\n")


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
        'B': 'NEUTRAL', 
        'C': 'LOW',
        'D': 'LOW'
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
        if rate_limiter.check_and_update(priority):
            # Forward packet via MQTT
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
    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
            
            with counts_lock:
                if not stats_queue.empty():
                    stats = stats_queue.get()
                    stats = list(stats.values())
                    # Extract just the message text
                    
                    # Call your ML model
                    print(stats)

                    pred = ml_model.predict(stats)
                    result = f"Predicted Bandwidths: HIGH={pred['HIGH']} Mbps, NEUTRAL={pred['NEUTRAL']} Mbps, LOW={pred['LOW']} Mbps"
                    #print(f"[ML Thread] ML Model Result: {result}\n")

        except Exception as e:
            print(f"[ML Thread] Error: {e}")

def sender_thread(client):
    print(f"\n[{DEVICE_NAME}] Type messages to send to HUB (topic: laptop1/inbox)")
    print("Press Ctrl+C to exit.\n")

    while True:
        try:
            input_msg = input()
            if input_msg.strip():
                if DEVICE_NAME == "laptop1":
                    # Laptop1 can send to laptop2 or laptop3
                    if input_msg.startswith("@laptop2 "):
                        actual_msg = input_msg[9:]  # Remove "@laptop2 "
                        print(actual_msg)
                        client.publish("laptop2/inbox", actual_msg)
                        print(f"[{DEVICE_NAME}] Sent to laptop2: {actual_msg}")
                    elif input_msg.startswith("@laptop3 "):
                        actual_msg = input_msg[9:]  # Remove "@laptop3 "
                        client.publish("laptop3/inbox", actual_msg)
                        print(f"[{DEVICE_NAME}] Sent to laptop3: {actual_msg}")
                    else:
                        print("Format: @laptop2 message OR @laptop3 message")
                else:
                    # Laptop2 and Laptop3 always send to laptop1
                    client.publish("laptop1/inbox", input_msg)
                    print(f"[{DEVICE_NAME}] Sent to laptop1: {input_msg}")
        except KeyboardInterrupt:
            print("Exiting sender thread...")
            break

'''
def udp_receiver_thread(listen_ip="0.0.0.0", listen_port=5005, buffer_size=65535):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))
    print(f"[{DEVICE_NAME}] UDP Receiver listening on {listen_ip}:{listen_port}")
    while True:
        data, addr = sock.recvfrom(buffer_size)

        # Extract tag (before the 'x' padding)
        try:
            decoded = data.decode("utf-8", errors="ignore")
            packet = decoded.split(":")
            tag = packet[0]
            content = packet[1].strip()
        except:
            tag = "<decode error>"

        print(f"[{DEVICE_NAME}] UDP From {addr[0]}:{addr[1]} | TYPE: {tag} | Size: {len(decoded)}")
'''
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

#Run Sender Thread
threading.Thread(target=client.loop_forever, daemon=True).start()
# Start UDP packet rerouter thread
threading.Thread(target=udp_packet_rerouter, args=(client,), daemon=True).start()
#start mqtt communication thread
threading.Thread(target=sender_thread, args=(client,), daemon=True).start()
# Start stats collector thread
threading.Thread(target=stats_collector_thread, daemon=True).start()
#ML Processing thread
threading.Thread(target=ml_processing_thread, args=(stats_queue, DEVICE_NAME), daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n[{DEVICE_NAME}] Exiting program...")