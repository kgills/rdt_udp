#! /usr/bin/env python

from rdt_defs import *

from random import randint

################################################################################
# Definitions


################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

print("UDP Server IP:", SERVER_IP)
print("UDP Server port:", SERVER_PORT)


sock.bind((SERVER_IP, SERVER_PORT))
while True:

    print("Waiting for new transfer")

    # Clear the data buffer
    data = bytearray()

    # Clear the crc_error flag
    crc_error = 0

    while True:

        # Receive packet from the client
        data_temp, addr = sock.recvfrom(PACKET_LEN)
        data_temp = bytearray(data_temp)

        if(crc_check(data_temp) != True):
            crc_error = 1
            print("CRC Error! packet_crc:", hex(crc), "calc_crc:",hex(crc_calc))
            break;


        # Simulate packet drop
        if(randint(0,100) != 1):

            # Simulate NACK
            if(randint(0,100) == 1):
                # Send NACK
                ack_packet = pack_packet(FLAGS_NACK, data_temp[SEQ_POS], 0)
            else:
                ack_packet = pack_packet(FLAGS_ACK, data_temp[SEQ_POS], 0)

            # Send the ACK
            sock.sendto(ack_packet, (CLIENT_IP, CLIENT_PORT))

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

