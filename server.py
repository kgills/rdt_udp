#! /usr/bin/env python
import socket
import signal
import sys

################################################################################
# Definitions

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

CRC_SEED = 0x1021
HEADER_LEN = 5
MSS = 100
PACKET_LEN = MSS+HEADER_LEN

FLAGS_POS = 0
FLAGS_FIN = 0x01

CRC_POS = 3

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

def signal_handler(signal, frame):
    print("\nClosing server")
    sock.close()
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

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

print("UDP Server IP:", UDP_IP)
print("UDP Server port:", UDP_PORT)


sock.bind((UDP_IP, UDP_PORT))
while True:

    # Clear the data buffer
    data = bytearray()

    # Clear the crc_error flag
    crc_error = 0

    while True:
        data_temp, addr = sock.recvfrom(PACKET_LEN)
        data_temp = bytearray(data_temp)

        # Check the CRC
        crc = (int(data_temp[CRC_POS]) << 8) + (int(data_temp[CRC_POS+1]) << 0)

        # Clear the CRC field before the calculation
        data_temp[CRC_POS] = 0
        data_temp[CRC_POS+1] = 0
        crc_calc = crc16(CRC_SEED, data_temp)
        if(crc_calc != crc):
            crc_error = 1
            print("CRC Error! packet_crc:", hex(crc), "calc_crc:",hex(crc_calc))
            break;

        # Add the data
        data += data_temp[5:]

        # Break if this is the last packet
        if ((data_temp[FLAGS_POS] & FLAGS_FIN) == FLAGS_FIN):
            break;

    if(crc_error == 0):
        print("Writing file")
        # Write byte array to file
        with open("output.png", 'wb') as output:
            output.write(data)

