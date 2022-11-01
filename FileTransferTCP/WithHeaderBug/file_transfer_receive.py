import socket
import logging
from collections import Counter
from time import sleep

SERVER_HOST = input("Enter the server host value:")  # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
# receive BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = 1500
HEADER_SIZE = 8
SEPARATOR = '<split>'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_: 
    # Using socket.SOCK_STREAM because the default protocol used is TCP
    # Using socket.AF_INET to use IPv4

    # Uses .connect() to connect to the server 
    socket_.connect((SERVER_HOST, SERVER_PORT))
    
    # Receiving file information
    filename, file_size = socket_.recv(1024).decode("ISO-8859-1").split(SEPARATOR)
    temp = socket_.recv(4)
    amount_packages = int.from_bytes(temp, "little")
    temp = socket_.recv(4)
    BUFFER_SIZE = int.from_bytes(temp, "little")
    temp = socket_.recv(4)
    HEADER_SIZE = int.from_bytes(temp, "little")

    header = []
    j = 0
    with open(filename, "wb") as file:
        while j < amount_packages:
            bytes_read = (socket_.recv(BUFFER_SIZE + HEADER_SIZE))
            sleep(0.000000000000000000000001)
            counter = int(bytes_read[:HEADER_SIZE].decode('ISO-8859-1'))
            package = bytes_read[HEADER_SIZE:]

            if counter == j:
                # write to the file the bytes we just received
                file.write(package)
                j += 1

            # if bytes_read:
            #     header.append(True)
            # else:
            #     header.append(False)

    #count = Counter(header)

    #packages_received = count[True]
    #packages_lost = count[False]
    print(f'{filename} recebido.')

    print(f'Encerrando conexão com o cliente')
    socket_.close()

    print(f'\nTamanho do Arquivo Transmitido: {file_size} bytes')
    #print(f'Número de Pacotes Recebidos: {packages_received}')
    #print(f'Número de Pacotes Perdidos: {packages_lost}')