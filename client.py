#! /usr/bin/env python
import socket
import signal
import sys

def signal_handler(signal, frame):
    sys.exit(0)

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python client.py <path_to_file> server_ip server_port"
if len(sys.argv) < 4:
    print usage
    sys.exit(1)

UDP_IP = sys.argv[2]
UDP_PORT = int(sys.argv[3])

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

# Get a byte array of the file
with open(sys.argv[1], "rb") as sendFile:
    f = sendFile.read()
    byteArray = bytearray(f)

print "Sending: ", byteArray

# Open the socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
# Send a test message
sock.sendto(byteArray, (UDP_IP, UDP_PORT))
