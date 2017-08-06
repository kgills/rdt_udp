from rdt_defs import *

################################################################################
# Definitions
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

def signal_handler(signal, frame):
    print("\nClosing server")
    sock.close()
    sys.exit(0)

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Parse the input arguments
usage = "python server.py output_file_name window"
if len(sys.argv) < 3:
    print(usage)
    sys.exit(1)

output_file = sys.argv[1]
window_size = int(sys.argv[2])

server_ip = "localhost"
print("UDP Server IP  :", server_ip)
print("UDP Server port:", SERVER_PORT)
print("output_file = ",output_file)

# Set the timeout, open the socket
sock.settimeout(SOCK_TIMEOUT)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((server_ip, SERVER_PORT))

# Initialize the window
window = []
for i in range(0,SEQ_SIZE):
    x = WindowElement()
    x.seq = i
    x.mult = 0
    x.state = STATE_UNACKED
    window.append(x)

recv_base = 0

print("Waiting for new transfer")

# Clear the data buffer
data = bytearray()
start = 1
receiving = 1
while(receiving == 1):

    ############################################################################
    # Process next ACK

    data_present = 0
    try:
        packet_data, addr = sock.recvfrom(PACKET_LEN) 
        data_present = 1 
    except socket.error:
        # No pending ACKS
        data_present = 0    

    if(data_present == 1):
        if(start == 1):
            print("Receiving the file")
            start = 0

        # Check the CRC
        if(crc_check(packet_data) != True):
            nack_packet = pack_packet(FLAGS_NACK, packet_data[SEQ_POS])
            sock.sendto(nack_packet, (addr))
            break

        # Check that the sequence number is in the window
        seq = packet_data[SEQ_POS]

        low_limit = recv_base - window_size
        if(low_limit < 0):
            low_limit = SEQ_SIZE + low_limit

        high_limit = recv_base - 1
        if(high_limit < 0):
            high_limit = SEQ_SIZE + high_limit

        if(((seq - low_limit)%(SEQ_SIZE)) <= ((high_limit - low_limit)%(SEQ_SIZE))):
            # Send ACK without saving the data
            ack_packet = pack_packet(FLAGS_ACK, packet_data[SEQ_POS])
            sock.sendto(ack_packet, (addr))
        
        else:

            low_limit = recv_base
            if(low_limit < 0):
                low_limit = SEQ_SIZE + low_limit

            high_limit = recv_base + window_size
            if(high_limit >= SEQ_SIZE):
                hight_limit = high_limit - SEQ_SIZE

            if(((seq - low_limit)%(SEQ_SIZE)) >= ((high_limit - low_limit)%(SEQ_SIZE))):
                # Drop the packet if outside the window size
                pass
                
            else:
                # Send ACK
                ack_packet = pack_packet(FLAGS_ACK, packet_data[SEQ_POS])
                sock.sendto(ack_packet, (addr))

                # Save the state
                window[seq].state = STATE_ACKED

                # Buffer the data
                window[seq].data = packet_data
                
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
        if(recv_base == SEQ_SIZE):
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
