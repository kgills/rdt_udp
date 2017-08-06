import socket
import signal
import sys

SERVER_PORT = 5005
CLIENT_PORT = 5006

# SOCK_TIMEOUT = 0.1 # 100 ms
SOCK_TIMEOUT = 0.0 # non-blocking

SEND_BASE_TIMEOUT_MS = 200

WINDOW_SIZE = 64
SEQ_SIZE = 3*WINDOW_SIZE

CRC_SEED = 0x1021
HEADER_LEN = 4
MSS = 100
PACKET_LEN = MSS+HEADER_LEN

FLAGS_POS = 0
FLAGS_FIN = 0x01
FLAGS_ACK = 0x02
FLAGS_NACK = 0x04

SEQ_POS = 1
CRC_POS = 2

def crc16(crc, data):
    msb = crc >> 8
    lsb = crc & 255
    for c in data:
        x = c ^ msb
        x ^= (x >> 4)
        msb = (lsb ^ (x >> 3) ^ (x << 4)) & 255
        lsb = (x ^ (x << 5)) & 255
    return (msb << 8) + lsb

def pack_packet(flags, seq, data=None):

    if(data == None):
        data = bytearray()
    else:
        data = bytearray(data)

    # Add in reverse order
    crc = 0
    data_temp = crc.to_bytes(2, 'big') + data
    data_temp = seq.to_bytes(1, 'big') + data_temp
    data_temp = flags.to_bytes(1, 'big') + data_temp

    # Calculate the CRC value
    crc = crc16(CRC_SEED, data_temp)

    # Replace the CRC Value
    data_temp = bytearray(data_temp)
    data_temp[CRC_POS] = (crc & 0xFF00) >> 8
    data_temp[CRC_POS+1] = (crc & 0x00FF) >> 0
    return data_temp

def crc_check(data):

    data = bytearray(data)

    # Save CRC from the data
    crc = (int(data[CRC_POS]) << 8) + (int(data[CRC_POS+1]) << 0)

    # Clear the CRC field before the calculation
    data[CRC_POS] = 0
    data[CRC_POS+1] = 0

    # Calculate and compare the crc values
    crc_calc = crc16(CRC_SEED, data)
    if(crc_calc != crc):
        return False

    return True

STATE_ACKED = 0
STATE_UNACKED = 1
STATE_USABLE = 2

class WindowElement:
    seq = 0
    mult = 0
    time_sent = 0
    state = STATE_USABLE
    data = bytearray()
