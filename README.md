# rdt_udp
Reliable data xfer over UDP.
Requires Python3.
Currently uses a sequential ACK to confirm receipt of data.

# Usage
Make sure the server is running before starting the client

	python3 server.py
	python3 client.py <path_to_file>

# Random file
dd if=/dev/urandom of=random.img count=1 bs=100k
