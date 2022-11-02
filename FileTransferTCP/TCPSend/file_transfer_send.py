from email import header
from tabnanny import filename_only

import socket
import os 
import time

SERVER_HOST = input("Enter the server host value:")  # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
SEPARATOR = '<split>'
# send BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = [500, 1000, 1500]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Using socket.SOCK_STREAM because the default protocol used is TCP
    # Using socket.AF_INET to use IPv4

    # The .bind() method is used to associate the socket with a specific network interface and port number
    server_socket.bind((SERVER_HOST, SERVER_PORT)) 
    
    # The .listen() method enables a server to accept connections.
    server_socket.listen(1) 
    # The .listen() method has a backlog parameter. 
    # It specifies the number of unaccepted connections that the system will allow before refusing new connections. 
    # Starting in Python 3.5, it’s optional. If not specified, a default backlog value is chosen.

    # The .accept() method blocks execution and waits for an incoming connection. 
    # When a client connects, it returns a new socket object representing the connection and a tuple holding
    # the address of the client.
    client_socket, addr = server_socket.accept()

    # One thing that’s imperative to understand is that you now have a new socket object from .accept(). 
    # This is important because it’s the socket that you’ll use to communicate with the client. 
    # It’s distinct from the listening socket that the server is using to accept new connections
    
    with client_socket:
        print(f'[-] Connected by {addr}')
        i = 0

        data = ""

        # the name of file we want to send, make sure it exists
        # The filename needs to exist in the current directory, 
        # or you can use an absolute path to that file somewhere on your computer.
        filename = input('Digite o nome do arquivo para enviar: ')
        
        # remove absolute path if there is
        filename_only = os.path.basename(filename)
        
        # Choosing the size of the buffer
        buffer_size_option = int(input(f'Digite a opção referente ao tamanho dos pacotes:\n1. 500 bytes \n2. 1000 bytes \n3. 1500 bytes\n'))
        if buffer_size_option == 1:
            i = 0
        elif buffer_size_option == 2:
            i = 1
        else:
            i = 2

        start = time.time()
        # get the file size
        file_size = os.path.getsize(filename)

        amount_packages = (file_size // BUFFER_SIZE[i]) + 1

        # Sending file information
        client_socket.send(f"{filename_only}{SEPARATOR}{file_size}".encode())
        client_socket.sendall(amount_packages.to_bytes(4, "little"))
        client_socket.sendall(BUFFER_SIZE[i].to_bytes(4, "little"))
        check_sent = client_socket.recv(1024).decode()

        # start sending the file
        with open(filename, "rb") as file:
            for j in range(amount_packages):
                # read the bytes from the file
                bytes_read = file.read(BUFFER_SIZE[i])

                # we use sendall to assure transmission in
                # busy networks
                client_socket.sendall(bytes_read)
                time.sleep(0.01)

        temp = client_socket.recv(4)
        header = int.from_bytes(temp, "little")
        client_socket.close()

    server_socket.close()

    end = time.time()
    total_time = end - start
    file_size_bit = file_size * 8

    speed = "{:,}".format(round(file_size_bit / total_time, 3)).replace('.','/')
    speed = speed.replace(',','.')
    speed = speed.replace('/',',')

    print(f'\nTamanho do Arquivo Transmitido: {file_size} bytes')
    print(f'Número de Pacotes Enviados: {amount_packages}')
    print(f'Tempo de transmissão:  {round(total_time, 4)} s')
    print(f'Velocidade de Transmissão: {speed} bit/s')  # bit / s



        

    
    