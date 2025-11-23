import paho.mqtt.client as mqtt
import threading
import time
import os
from collections import defaultdict
import socket
import queue


BROKER_IP = "10.141.41.70"   # HUB IP
DEVICE_NAME = ""             # laptop1, laptop2, laptop3

packet_counts = defaultdict(int)
counts_lock = threading.Lock()

# Queue for sending counts to processing thread
stats_queue = queue.Queue()

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

def udp_packet_rerouter(client, listen_ip="0.0.0.0", listen_port=5005, buffer_size=65535):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))
    print(f"[{DEVICE_NAME}] UDP Receiver listening on {listen_ip}:{listen_port}")
    
    while True:
        data, addr = sock.recvfrom(buffer_size)
        try:
            decoded = data.decode("utf-8", errors="ignore")
            packet = decoded.split(":")
            tag = packet[0]
            content = packet[1].strip()
        except:
            tag = "<decode error>"
        
        with counts_lock:
            packet_counts[tag] += 1

        # Reroute packet content via MQTT
        rerouter(client, tag, content, data)

def rerouter(client, tag, content, raw_data):
    if(DEVICE_NAME != "laptop1"):
        return  # Only laptop1 reroutes packets

    # Tag to topic mapping
    tag_routing = {
        "A": "laptop1/inbox",
        "B": "laptop2/inbox",
        "C": "laptop3/inbox",
        "D": "laptop4/inbox"
    }
    
    # Get target topic from mapping
    target_topic = tag_routing.get(tag)
    
    if target_topic:
        client.publish(target_topic, content)
        print(f"[{DEVICE_NAME}] Rerouted UDP packet to {target_topic} | TYPE: {tag} | Size: {len(raw_data)}")
    else:
        print(f"[{DEVICE_NAME}] Unknown tag '{tag}' - no routing rule")

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

# Run sender in main thread
#sender_thread(client)

udp_receiver_thread()