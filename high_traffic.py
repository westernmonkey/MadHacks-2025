import socket
import time
import argparse

def send_udp_packets(target_ip, target_port, packet_size, pps, duration, tag):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload_base = tag.encode() + b":"  # Tag prefix + colon as delimiter
    
    # The rest of the packet is filled with 'x' bytes
    filler_size = max(0, packet_size - len(payload_base))
    packet = payload_base + b'x' * filler_size

    end_time = time.time() + duration
    sent_packets = 0
    sent_bytes = 0
    interval = 1.0 / pps if pps > 0 else 0

    print(f"Sending UDP packets to {target_ip}:{target_port} with tag '{tag}'")
    print(f"Packet size: {packet_size}, Rate: {pps} pps, Duration: {duration}s\n")

    last_report = time.time()

    while time.time() < end_time:
        sock.sendto(packet, (target_ip, target_port))
        sent_packets += 1
        sent_bytes += len(packet)

        if interval > 0:
            time.sleep(interval)

        now = time.time()
        if now - last_report >= 1.0:
            print(f"Sent {sent_packets} packets ({sent_bytes} bytes) in last {now - last_report:.2f} seconds")
            sent_packets = 0
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
    parser.add_argument("--tag", type=str, default="TAG", help="Tag string to include in packets")

    args = parser.parse_args()

    send_udp_packets(args.ip, args.port, args.size, args.pps, args.duration, args.tag)
