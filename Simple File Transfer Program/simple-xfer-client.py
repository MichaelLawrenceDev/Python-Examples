# Socket File Transfer Example
# This program implements the client side of a simple file transfer protocol
# This protocol only allows for a file transfer from the client to the server
# The network communication protocol is as follows:
#   client: Sending N Bytes
#   server: READY TO RECEIVE
#   client: transfer file of size N bytes
#   server: FILE RECEIVED

import socket
import sys

# ensure we received appropriate number of arguments
if len(sys.argv) != 2:
    print('Usage: python3 simple-xfer-client.py <file to send>')
    sys.exit(0)

filename = sys.argv[1]

# create an IPv4 TCP socket to connect to a server implementing this protocol
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 5225
print('Connecting to {0}:{1} to send file: {2}'.format(host, port, filename))
s.connect((host, port))

# read the contents of the file (as binary) we want to send
with open(filename, 'rb') as f:
    data = f.read()

# send the initial protocol message: Sending N Bytes
message = 'Sending {0} Bytes'.format(len(data))
s.send(message.encode())

# once that is sent, we expect a reply of READY TO RECEIVE from the server
print('Message sent. Awaiting reply from server')
reply = s.recv(1024)
if reply.decode() != 'READY TO RECEIVE':
    print("Network Protocol Failure: incorrect response from server")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit(-1)

# time to send the file
bytes_sent = 0
print('Preparing to send {0} bytes'.format(len(data)))

# this code is written to send the file in pieces if needed
# if the system isn't particularly busy or the file not ridiculously large, a single send call is likely sufficient
while bytes_sent < len(data):
    sent = s.send(data[bytes_sent:])
    if sent == 0:
        print("Socket Connection Broken")
        sys.exit(-2)
    bytes_sent += sent
    print('\tSent {0} bytes'.format(sent))


print('Waiting for confirmation that entire file was received....')
reply = s.recv(1024)

# realistically, TCP should ensure the file arrives correctly but confirmations are still nice
if reply.decode() != 'FILE RECEIVED':
    print('{0} failed to send correctly'.format(filename))
    # if the file did not send correctly, we could attempt to send it again if we chose
else:
    print('File received correctly')
print('Shutting down connection with {0}:{1}'.format(host,port))
s.shutdown(socket.SHUT_RDWR)
s.close()

