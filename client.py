#! /usr/bin/env python
import socket
import signal
import sys

################################################################################
# Definitions

def signal_handler(signal, frame):
    sys.exit(0)

def crc16(crc, data):
    msb = crc >> 8
    lsb = crc & 255
    for c in data:
        x = c ^ msb
        x ^= (x >> 4)
        msb = (lsb ^ (x >> 3) ^ (x << 4)) & 255
        lsb = (x ^ (x << 5)) & 255
    return (msb << 8) + lsb

CRC_SEED = 0x1021
HEADER_LEN = 5

HEADER_LEN = 5
MSS = 100
PACKET_LEN = MSS+HEADER_LEN

FLAGS_POS = 0
FLAGS_FIN = 0x01

CRC_POS = 3

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python client.py <path_to_file> server_ip server_port"
if len(sys.argv) < 4:
    print(usage)
    sys.exit(1)

UDP_IP = sys.argv[2]
UDP_PORT = int(sys.argv[3])

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)

# Get a byte array of the file
with open(sys.argv[1], "rb") as sendFile:
    f = sendFile.read()
    data = bytearray(f)

data_len = len(data)
i = 0
pos = 0

while(i < data_len):

    # Isolate the packet
    i += MSS
    data_temp = bytearray(data[pos:i])
    pos = i

    # Add the header
    if(i >= data_len):
        flags = FLAGS_FIN
    else:
        flags = 0
    seq = 0
    window = 0
    crc = 0

    # Add in reverse order
    data_temp = crc.to_bytes(2, 'big') + data_temp
    data_temp = window.to_bytes(1, 'big') + data_temp
    data_temp = seq.to_bytes(1, 'big') + data_temp
    data_temp = flags.to_bytes(1, 'big') + data_temp

    crc = crc16(CRC_SEED, data_temp)

    # Replace the CRC Value
    data_temp = bytearray(data_temp)
    data_temp[CRC_POS] = (crc & 0xFF00) >> 8
    data_temp[CRC_POS+1] = (crc & 0x00FF) >> 0

    # Open the socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    # Send the packet
    sock.sendto(data_temp, (UDP_IP, UDP_PORT))

print("Done sending file")
sock.close()