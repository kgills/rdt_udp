import signal
import sys
import subprocess

################################################################################
# Definitions
MSS_START = 25
MSS_END = 100
MSS_INC = 25

PROP_DELAY_START = 0
PROP_DELAY_END = 500
PROP_DELAY_INC = 100

PROP_VAR = 5

DROP_START = 0
DROP_END = 20
DROP_INC = 5

WINDOW_START = 4
WINDOW_END = 64
WINDOW_INC = 20

RESULTS_FILE="results.txt"

def signal_handler(signal, frame):
    print("\nClosing launcher")
    sock.close()
    sys.exit(0)

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

################################################################################
# Main

signal.signal(signal.SIGINT, signal_handler)

# Create the results file
file = open(RESULTS_FILE,"w") 
file.write("len, loss, latency, variance, mss, elapsed, bps, window\n")
file.close() 

# Start the loops
for delay in my_range(PROP_DELAY_START, PROP_DELAY_END, PROP_DELAY_INC):
    for drop in my_range(DROP_START, DROP_END, DROP_INC):
        # Set the network prop delay, variance, and drop

        for mss in my_range(MSS_START, MSS_END, MSS_INC):
            for window in my_range(WINDOW_START, WINDOW_END, WINDOW_INC):

                # print(mss, delay, drop, window)

                # Start the server
                server_command = "python3 server.py random_out.img "+str(window)
                print(server_command)
                server_process = subprocess.Popen(server_command, shell=True, stdout=subprocess.PIPE)
                
                # Start the Client
                client_command = "python3 client.py random.img "+str(drop)+" "+str(delay)+" "+str(PROP_VAR)+" "+str(mss)+" "+str(window)+" >> "+str(RESULTS_FILE)
                print(client_command)
                client_process = subprocess.Popen(client_command, shell=True, stdout=subprocess.PIPE)

                # Wait for the client
                client_process.wait()

                # Close the server
                server_process.kill()


