from rdt_defs import *
import datetime
import time

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

server_ip = "localhost"
print("UDP Server IP  :", server_ip)
print("UDP Server port:", SERVER_PORT)
print("UDP Client port:", CLIENT_PORT)

# Setup listener for the ACK packets from the server
sock.bind((server_ip, CLIENT_PORT))

# Set the timeout
sock.settimeout(SOCK_TIMEOUT)

# Initialize the window
window = []
for i in range(0,WINDOW_SIZE*2):
    x = WindowElement()
    x.seq = i
    x.mult = 0
    x.time_sent = datetime.datetime.now()
    x.state = STATE_USABLE
    window.append(x)

# Get a byte array of the file
with open(sys.argv[1], "rb") as sendFile:
    f = sendFile.read()
    data = bytearray(f)

data_len = len(data)
print("Data_len =",data_len)

# Initialize the send_base
send_base = 0
sending = 1

while(sending == 1):

    ################################################################################
    # Send as many packets as we can

    for i in range(0, WINDOW_SIZE):

        # Wrap the window pointer
        j = send_base + i
        if(j >= 2*WINDOW_SIZE):
            j = j - 2*WINDOW_SIZE

        if(window[j].state == STATE_USABLE):

            # Find the piece of data we need to send
            data_start = (window[j].mult*2*WINDOW_SIZE + window[j].seq)*MSS
            data_end = data_start + MSS
            data_temp = bytearray(data[data_start:data_end])

            # See if we have sent all of the data
            if(data_start >= data_len):
                break

            # Create the header elements
            if(data_end >= data_len):
                flags = FLAGS_FIN
            else:
                flags = 0

            data_temp = pack_packet(flags, window[j].seq, data_temp)

            # Send the packet
            sock.sendto(data_temp, (server_ip, SERVER_PORT))

            # Save the state
            window[j].state = STATE_UNACKED
            window[j].time_sent = datetime.datetime.now()

    ################################################################################
    # Process the ACKs
    while True:

        try:
            ack_data, addr = sock.recvfrom(PACKET_LEN)  
        except socket.error:
            # No pending ACKS
            break

        # Check the CRC
        if(crc_check(ack_data) != True):
            continue
          
        # Resend if it's not an ack packet
        elif((ack_data[FLAGS_POS] & FLAGS_ACK) != FLAGS_ACK):
            
            # Resend the packet

            # Find the piece of data we need to send
            j = ack_data[SEQ_POS]
            data_start = (window[j].mult*2*WINDOW_SIZE + window[j].seq)*MSS
            data_end = data_start + MSS
            data_temp = bytearray(data[data_start:data_end])

            # Create the header elements
            if(data_end >= data_len):
                flags = FLAGS_FIN
            else:
                flags = 0

            data_temp = pack_packet(flags, window[j].seq, data_temp)

            # Send the packet
            sock.sendto(data_temp, (server_ip, SERVER_PORT))

            # Save the state
            window[j].time_sent = datetime.datetime.now()

        # Register the ACK
        else:
            j = ack_data[SEQ_POS]
            window[j].state = STATE_ACKED

    ################################################################################
    # Advanse the send_base

    while(window[send_base].state != STATE_USABLE):

        if(window[send_base].state == STATE_UNACKED):

            # See if the send_base has timed out
            now = datetime.datetime.now()
            elapsed = (now - window[send_base].time_sent).total_seconds() * 1000     # convert S to MS
            if(int(elapsed) > SEND_BASE_TIMEOUT_MS):

                # Find the piece of data we need to send
                j = send_base
                data_start = (window[j].mult*2*WINDOW_SIZE + window[j].seq)*MSS
                data_end = data_start + MSS
                data_temp = bytearray(data[data_start:data_end])

                # Create the header elements
                if(data_end >= data_len):
                    flags = FLAGS_FIN
                else:
                    flags = 0

                data_temp = pack_packet(flags, window[j].seq, data_temp)

                # Send the packet
                sock.sendto(data_temp, (server_ip, SERVER_PORT))

                # Save the state
                window[j].time_sent = datetime.datetime.now()
                
        elif(window[send_base].state == STATE_ACKED):

            # See if we're done sending the file
            data_start = (window[send_base].mult*2*WINDOW_SIZE + window[send_base].seq)*MSS
            data_end = data_start + MSS

            if(data_end >= data_len):
                sending = 0

            # Advance the send_base
            window[send_base].state = STATE_USABLE
            window[send_base].mult = window[send_base].mult+1

            send_base = send_base+1
            if(send_base >= 2*WINDOW_SIZE):
                send_base = send_base - 2*WINDOW_SIZE


print("Done sending file")
sock.close()
