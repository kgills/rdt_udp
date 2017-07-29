#! /usr/bin/env python

from rdt_defs import *
import datetime

################################################################################
# Definitions

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python client.py server_ip <path_to_file>"
if len(sys.argv) < 3:
    print(usage)
    sys.exit(1)

server_ip = sys.argv[1]
print ("UDP Server IP:", server_ip)
print("UDP Client port:", CLIENT_PORT)

# Setup listener for the ACK packets from the server
sock.bind(("localhost", CLIENT_PORT))

# Set the timeout
sock.settimeout(SOCK_TIMEOUT)

# Initialize the window
window = []
for i in range(0,256):
    x = WindowElement()
    x.seq = i
    x.time_sent = datetime.datetime.now()
    if(i < WINDOW_SIZE):
        x.state = STATE_USABLE
    else:
        x.state = STATE_UNUSABLE
    window.append(x)

# elapsed = end - start
# print(elapsed.total_seconds())

# Get a byte array of the file
with open(sys.argv[2], "rb") as sendFile:
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
        sock.sendto(data_temp, (server_ip, SERVER_PORT))

        # Wait for an ACK
        try:
            ack_data, addr = sock.recvfrom(PACKET_LEN)  
        except socket.timeout:
            print("Timed out waiting for ACK")
            continue

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

    # Update the sequence number
    seq += 1
    if(seq == 256):
        seq = 0


print("Done sending file")
sock.close()
