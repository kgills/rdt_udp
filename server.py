#! /usr/bin/env python

from rdt_defs import *
from random import randint

################################################################################
# Definitions

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

print("UDP Server port:", SERVER_PORT)

sock.bind(("localhost", SERVER_PORT))
while True:

    print("Waiting for new transfer")

    # Clear the data buffer
    data = bytearray()

    # Clear the sequence number
    seq_exp = 0

    while True:

        # Receive packet from the client
        data_temp, addr = sock.recvfrom(PACKET_LEN)
        data_temp = bytearray(data_temp)

        if(crc_check(data_temp) != True):
            print("CRC Error! packet_crc:", hex(crc), "calc_crc:",hex(crc_calc))

            # Send NACK for this packet
            ack_packet = pack_packet(FLAGS_MACK, data_temp[SEQ_POS], 0)
            sock.sendto(ack_packet, (addr))
            continue

        elif(data_temp[SEQ_POS] != seq_exp):
            print("SEQ mismatch! seq_exp:", hex(seq_exp), "seq_rec:",hex(data_temp[SEQ_POS]))

            # ACK last good packet
            ack_packet = pack_packet(FLAGS_ACK, seq_exp-1, 0)
            sock.sendto(ack_packet, (addr))
            continue

        else:
            # ACK this packet
            ack_packet = pack_packet(FLAGS_ACK, data_temp[SEQ_POS], 0)
            sock.sendto(ack_packet, (addr))

        # Add the data
        data += data_temp[5:]

        # Break if this is the last packet
        if ((data_temp[FLAGS_POS] & FLAGS_FIN) == FLAGS_FIN):
            break;

        # Advance the sequence number expected
        seq_exp += 1
        if(seq_exp == 256):
            seq_exp = 0


    print("Writing file")
    # Write byte array to file
    with open("output.png", 'wb') as output:
        output.write(data)

