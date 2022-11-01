import socket
import os 
import logging
from collections import Counter

SERVER_HOST = input("Enter the server host value:")  # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
# receive BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = 1500
SEPARATOR = '<split>'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_: 
    # Using socket.SOCK_STREAM because the default protocol used is TCP
    # Using socket.AF_INET to use IPv4

    # Uses .connect() to connect to the server 
    socket_.connect((SERVER_HOST, SERVER_PORT))
    
    # Receiving file information
    filename, file_size = socket_.recv(1024).decode().split(SEPARATOR)
    #print(f'[{filename}]\n[{file_size}]')
    temp = socket_.recv(4)
    amount_packages = int.from_bytes(temp, "little")
    temp = socket_.recv(4)
    BUFFER_SIZE = int.from_bytes(temp, "little")

    received_message = 'received'
    socket_.send(received_message.encode())

    header = []
    with open(filename, "wb") as file:
        for j in range(amount_packages):
            bytes_read = socket_.recv(BUFFER_SIZE)
            
            # write to the file the bytes we just received
            file.write(bytes_read)

            if bytes_read:
                header.append(True)
            else:
                header.append(False) 


    count = Counter(header)

    packages_received = count[True]
    packages_lost = count[False]
    print(f'{filename} recebido.')
    socket_.sendall((packages_received).to_bytes(4, "little"))

    print(f'Encerrando conexão com o cliente')
    socket_.close()

    print(f'\nTamanho do Arquivo Transmitido: {file_size} bytes')
    print(f'Número de Pacotes Recebidos: {packages_received}')
    print(f'Número de Pacotes Perdidos: {packages_lost}')