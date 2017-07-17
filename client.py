#! /usr/bin/env python

from rdt_defs import *

################################################################################
# Definitions

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python client.py <path_to_file>"
if len(sys.argv) < 2:
    print(usage)
    sys.exit(1)

print ("UDP Server IP:", SERVER_IP)
print ("UDP Server port:", SERVER_PORT)

print("UDP Client IP:", CLIENT_IP)
print("UDP Client port:", CLIENT_PORT)

# Setup listener for the ACK packets from the server
sock.bind((CLIENT_IP, CLIENT_PORT))

# Get a byte array of the file
with open(sys.argv[1], "rb") as sendFile:
    f = sendFile.read()
    data = bytearray(f)

data_len = len(data)
i = 0
pos = 0
seq = 0

while(i < data_len):

    # Isolate the packet
    i += MSS
    data_temp = bytearray(data[pos:i])
    pos = i

    # Create the header elements
    if(i >= data_len):
        flags = FLAGS_FIN
    else:
        flags = 0
    window = 0

    data_temp = pack_packet(flags, seq, window, data_temp)

    while True:
        # Send the packet
        sock.sendto(data_temp, (SERVER_IP, SERVER_PORT))

        # Wait for an ACK
        ack_data, addr = sock.recvfrom(PACKET_LEN)

        # Check the CRC
        if(crc_check(ack_data) != True):
            print("Error CRC")
            continue
        # Resend if it's not an ack packet
        if((ack_data[FLAGS_POS] & FLAGS_ACK) != FLAGS_ACK):
            print("Error NACK")
            continue
        # Resend if the sequence number doesn't match
        if(ack_data[SEQ_POS] != seq):
            print("Error SEQ Mismatch")
            continue

        break

    seq += 1


print("Done sending file")
sock.close()
