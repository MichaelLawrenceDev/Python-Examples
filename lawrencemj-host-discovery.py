
import threading
import queue
import ipaddress
import struct
import socket
import sys
# Michael Lawrence
# CSC 435-001
# 3/5/2020

# Starts sniffing for correct ICMP packets with the msg message
def ICMP_sniffer(port, msg, live_queue):
        
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    s.bind(("0.0.0.0", 1))
    #s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    print("socket created, waiting for packets")
    while 1:
        recPacket, addr = s.recvfrom(1024)
        icmp_header = recPacket[20:28]
        type, code, checksum, p_id, sequence = struct.unpack('bbHHh', icmp_header)
        print("type: [" + str(type) + "] code: [" + str(code) + "] checksum: [" + str(checksum) + "] p_id: [" + str(p_id) + "] sequence: [" + str(sequence) + "]")        

# Sends a UDP request to specified ip address with the message msg.
def ping(ip, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(msg.encode(), (str(ip), port))
    print("Message sent to IP: %s" % ip)

# Check if arguments are valid.
if len(sys.argv) != 2:
    print("./lawrencemj-host-discovery-1.py <IP address>")
    sys.exit(0)
try:
    Network_Flag = True
    if "/" in sys.argv[1]:
        address = ipaddress.ip_network(sys.argv[1], strict=False)
    else:
        Network_Flag = False
        address = ipaddress.ip_address(sys.argv[1])
except ValueError as e:
    print("Invalid IP format entered")
    sys.exit(0)

msg = "CSC-435-001 Live IP Check"
port = 32543
# Setting up sniffer
live_queue = queue.Queue()
sniffer_thread = threading.Thread(target=ICMP_sniffer, args=(port, msg, live_queue))
sniffer_thread.start()

# Send UDP packet to specified host or network
if Network_Flag:
    for ip in address.hosts():
        ping(ip, port, msg)
else:
    ping(address, port, msg)
