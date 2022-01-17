# Socket File Transfer Example
# This program implements the server side of a simple file transfer protocol
# This protocol only allows for a file transfer from the client to the server
# The network communication protocol is as follows:
#   client: Sending N Bytes
#   server: READY TO RECEIVE
#   client: transfer file of size N bytes
#   server: FILE RECEIVED

import socket

# create an IPv4 TCP socket to listen on port 5225
host = '127.0.0.1'
port = 5225

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
s.listen(1)
print('Started server listening on {0}:{1}'.format(host, port))

try:
    while True:
        # create a socket to communicate with the client when we receive a connection
        clientsocket, address = s.accept()
        print('\nReceived connection from {0}:{1}'.format(address[0], address[1]))

        # The first thing we expect is a message indicating it is time to receive a file
        # The message should be: Sending N Bytes.
        # We will parse out the N to determine how many bytes to expect
        message = clientsocket.recv(1024)

        message = message.decode()

        # split the message. Assuming it is formatted correctly, the 2nd entry
        print('\tReceived initial protocol message: {0}'.format(message))
        split_message = message.split(' ')
        if split_message[0] == 'Sending' and split_message[2] == 'Bytes':
            try:
                # the 2nd part of the message should contain the number of bytes
                filesize = int(split_message[1])
                # since the first message was correct, reply with READY TO RECEIVE
                # this will indicate to the client it is time to transfer the file
                print('\tSending reply: READY TO RECEIVE')
                clientsocket.send(b'READY TO RECEIVE')
            except ValueError as e:
                # exception thrown here means it could not convert to an int
                print(e)
                continue
        
        bytes_received = 0
        # list to hold the parts of the file while we reassemble
        buffer = []
        print('\tPreparing to receive {0} bytes'.format(filesize))
        try:
            while bytes_received < filesize:
                chunk = clientsocket.recv(4096)
                if chunk == b'':
                    raise RuntimeError('Socket Connection Broken')
                bytes_received += len(chunk)
                print('\t\tReceived {0} bytes so far'.format(bytes_received))
                buffer.append(chunk)
        except:
            clientsocket.close()

        # join the individual byte strings into a single piece of data
        data = b''.join(buffer)
        print('\tSending confirmation to client: FILE RECEIVED')
        clientsocket.send(b'FILE RECEIVED')

        # write data to a file
        filename = 'test.file'
        print('\tWriting {0} bytes to file {1}'.format(bytes_received, filename))
        with open(filename, 'wb') as f:
            f.write(data)

        print('\tShutting down connection with {0}:{1}'.format(address[0], address[1]))
        clientsocket.shutdown(socket.SHUT_RDWR)
        clientsocket.close()

except KeyboardInterrupt:
    print('\n############ Closing Server ############')
    try:
        clientsocket.close()
    except:
        pass
    
