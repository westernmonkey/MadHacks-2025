import paho.mqtt.client as mqtt
import threading
import time

BROKER_IP = "10.141.41.70"   # HUB IP
DEVICE_NAME = ""             # laptop2, laptop3
PACKET_COUNT = 100           # Number of packets per latency check
counter = 0
byte_count = 0

# -----------------------------
# ASK USER WHICH DEVICE THIS IS
# -----------------------------
while DEVICE_NAME not in ["laptop2", "laptop3"]:
    DEVICE_NAME = input("Enter device name (laptop2 / laptop3): ").strip()

LAPTOP = DEVICE_NAME[-1]
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

def reporter_thread(client):
   global byte_count
   print(f"[{DEVICE_NAME}] 📊 Background Reporting Active...")
  
   while True:
       time.sleep(1.0) # Wait 1 second
      
       # Calculate Bandwidth (Bytes -> Megabits)
       mbps = (byte_count * 23) / 1_000_000
      
       # Send to Laptop 1 (The Brain)
       client.publish(OUTBOX_TOPIC, f"{LAPTOP}M" + str(mbps))
       print(f"[{DEVICE_NAME}] Sent to laptop1: {LAPTOP}M{mbps}")
      
       # Optional: Debug print if traffic is flowing
       # if stats["packet_count"] > 0:
       #     print(f"   (Debug) Sent stats: {report['mbps']} Mbps")


       # Reset for next second
       byte_count = 0

def on_message(client, userdata, msg):
    t1 = time.time()
    global counter
    global byte_count
    byte_count += 1
    message = msg.payload.decode()
    print(f"\n[{DEVICE_NAME}] Received on {msg.topic}: {message}")

    # Example server usage
    if message[0] == 'A':
        num1 = int(message[3:7])
        num2 = int(message[7:11])
        sum = num1 + num2
        time.sleep(0.000001)
    if message[0] == 'B':
        num1 = int(message[3:7])
        num2 = int(message[7:11])
        diff = num1 - num2
        time.sleep(0.000001)
    if message[0] == 'C':
        num1 = int(message[3:7])
        num2 = int(message[7:11])
        product = num1 * num2
        time.sleep(0.000001)

    if counter == 0:
        sender_thread(client, t1)
    counter = (counter + 1) % PACKET_COUNT
    # Save message to a file
    #with open(SAVE_FILE, "a") as f:
     #   f.write(f"{time.ctime()} - {msg.topic}: {message}\n")


# -----------------------------
# SENDER THREAD
# -----------------------------
def sender_thread(client, t1):
    # print(f"\n[{DEVICE_NAME}] Type messages to send to HUB (topic: laptop1/inbox)")
    # print("Press Ctrl+C to exit.\n")

    
    try:
        input_msg = time.time() - t1
        # Laptop2 and Laptop3 always send to laptop1
        client.publish("laptop1/inbox", f"{LAPTOP}L" + str(input_msg))
        print(f"[{DEVICE_NAME}] Sent to laptop1: {LAPTOP}L{input_msg}")
    except KeyboardInterrupt:
        print("Exiting sender thread...")

# -----------------------------
# MAIN PROGRAM
# -----------------------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"[{DEVICE_NAME}] Connecting to broker at {BROKER_IP}...")
client.connect(BROKER_IP, 1883, 60)

# Run MQTT loop in a background thread
threading.Thread(target=client.loop_forever, daemon=True).start()

# Run sender in main thread
reporter_thread(client)