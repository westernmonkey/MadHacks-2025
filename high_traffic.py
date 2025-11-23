import socket
import time
import argparse
import random

class Packet:
    def __init__(self, ptype: str):
        self.ptype = ptype  # e.g., 'VIP', 'NORMAL', etc.

    def build_payload(self, total_size: int) -> bytes:
        """
        Construct the full packet payload including the type and content.
        Format: TYPE:content + padding to total_size bytes
        """
        base = f"{self.ptype} :".encode('utf-8')
        padding_size = max(0, total_size - len(base))
        return base + f'{random.randint(11111111,99999999)}'.encode('utf-8')


def send_udp_packets(target_ip, target_port, packet_size, pps, duration, tags):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    

    end_time = time.time() + duration
    sent_packets = 0
    sent_bytes = 0
    interval = 1.0 / pps if pps > 0 else 0

    print(f"Sending UDP packets to {target_ip}:{target_port} with tags '{tags}'")
    print(f"Packet size: {packet_size}, Rate: {pps} pps, Duration: {duration}s\n")

    last_report = time.time()

    while time.time() < end_time:
        tag = random.choice(tags)   # pick a random tag from list
        packet_obj = Packet(tag)    # create a Packet instance
        packet = packet_obj.build_payload(packet_size)
        sock.sendto(packet, (target_ip, target_port))
        sent_packets += 1
        sent_bytes += len(packet)

        if interval > 0:
            time.sleep(interval)

        now = time.time()
        if now - last_report >= 1.0:
            print(f"Sent {sent_packets} packets ({sent_bytes} bytes) in last {now - last_report:.2f} seconds")
            sent_bytes = 0
            last_report = now

    print("Finished sending packets.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-speed UDP traffic sender with tag")
    parser.add_argument("--ip", type=str, required=True, help="Target IP address")
    parser.add_argument("--port", type=int, required=True, help="Target UDP port")
    parser.add_argument("--size", type=int, default=512, help="Packet size in bytes (default 512)")
    parser.add_argument("--pps", type=int, default=1000, help="Packets per second (default 1000)")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds (default 10)")
    parser.add_argument("--tags", type=str, default="TAG", help="Tag string to include in packets")

    args = parser.parse_args()
    args.tags = [tag.strip() for tag in args.tags.split(',')]

    send_udp_packets(args.ip, args.port, args.size, args.pps, args.duration, args.tags)

