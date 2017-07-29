from rdt_defs import *

################################################################################
# Definitions

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python server.py output_file_name"
if len(sys.argv) < 2:
    print(usage)
    sys.exit(1)

output_file = sys.argv[1]
server_ip = "localhost"
print("UDP Server IP  :", server_ip)
print("UDP Server port:", SERVER_PORT)
print("output_file = ",output_file)

# Set the timeout, open the socket
sock.settimeout(SOCK_TIMEOUT)
sock.bind((server_ip, SERVER_PORT))

# Initialize the window
window = []
for i in range(0,WINDOW_SIZE*2):
    x = WindowElement()
    x.seq = i
    x.mult = 0
    x.state = STATE_UNACKED
    window.append(x)

recv_base = 0

print("Waiting for new transfer")

# Clear the data buffer
data = bytearray()

receiving = 1
while(receiving == 1):

    ############################################################################
    # Process the ACKs
    while True:

        try:
            packet_data, addr = sock.recvfrom(PACKET_LEN)  
        except socket.error:
            # No pending ACKS
            break

        send_nack = 0

        # Check the CRC
        if(crc_check(packet_data) != True):
            send_nack = 1

        # Check that the sequence number is in the window
        elif((packet_data[SEQ_POS] > (window[recv_base].seq + WINDOW_SIZE)) or
            (packet_data[SEQ_POS] < window[recv_base].seq)):

            send_nack = 1

        # Send ACK
        else:
            ack_packet = pack_packet(FLAGS_ACK, packet_data[SEQ_POS])
            sock.sendto(ack_packet, (addr))

            # Save the state
            window[packet_data[SEQ_POS]].state = STATE_ACKED

            # Buffer the data
            window[packet_data[SEQ_POS]].data = packet_data

        if(send_nack == 1):
            nack_packet = pack_packet(FLAGS_NACK, packet_data[SEQ_POS])
            sock.sendto(ack_packet, (addr))

    ############################################################################
    # Advance the RECV base

    while(window[recv_base].state == STATE_ACKED):

        # Deliver the data
        data += window[recv_base].data[HEADER_LEN:]

        # See if we've received everything
        if((window[recv_base].data[FLAGS_POS] & FLAGS_FIN) == FLAGS_FIN):
            receiving = 0
            break

        # Save the state
        window[recv_base].state = STATE_UNACKED

        # Advance the recv base
        recv_base = recv_base + 1
        if(recv_base == 2*WINDOW_SIZE):
            recv_base = 0
            
print("Writing file")
# Write byte array to file
with open(output_file, 'wb') as output:
    output.write(data)

print("Acking remaining packets")
# ACK any remaining packets
while True:
    sock.settimeout(None)
    packet_data, addr = sock.recvfrom(PACKET_LEN)
    ack_packet = pack_packet(FLAGS_ACK, packet_data[SEQ_POS])
    sock.sendto(ack_packet, (addr))