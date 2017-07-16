#! /usr/bin/env python
import socket
import signal
import sys

def signal_handler(signal, frame):
    print "Closing server"
    sys.exit(0)


################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print "UDP Server IP:", UDP_IP
print "UDP Server port:", UDP_PORT

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "Received: ", data

    # Write byte array to file
    with open("output.txt", 'wb') as output:
        output.write(data)
