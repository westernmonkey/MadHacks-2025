import paho.mqtt.client as mqtt
import threading

BROKER_IP = "10.141.41.70"   # HUB IP
DEVICE_NAME = ""             # laptop2, laptop3

# -----------------------------
# ASK USER WHICH DEVICE THIS IS
# -----------------------------
while DEVICE_NAME not in ["laptop2", "laptop3"]:
    DEVICE_NAME = input("Enter device name (laptop2 / laptop3): ").strip()

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
def sender_thread(client):
    print(f"\n[{DEVICE_NAME}] Type messages to send to HUB (topic: laptop1/inbox)")
    print("Press Ctrl+C to exit.\n")

    while True:
        try:
            input_msg = input().strip()
            # Laptop2 and Laptop3 always send to laptop1
            client.publish("laptop1/inbox", input_msg)
            print(f"[{DEVICE_NAME}] Sent to laptop1: {input_msg}")
        except KeyboardInterrupt:
            print("Exiting sender thread...")
            break

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
sender_thread(client)
