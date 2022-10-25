from email import header
import socket
# from tabnanny import filename_only
import tqdm
import os
import time

SERVER_HOST = input("Enter the server host value:")  # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
SEPARATOR = '<split>'
# send BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = [500, 1000, 1500]

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    # Using socket.DGRAM because the default protocol used is UDP
    # Using socket.AF_INET to use IPv4

    i = 0

    data = ""

    # the name of file we want to send, make sure it exists
    # The filename needs to exist in the current directory,
    # or you can use an absolute path to that file somewhere on your computer.
    filename = input('Digite o nome do arquivo para enviar: ')

    # remove absolute path if there is
    filename_only = os.path.basename(filename)

    # Choosing the size of the buffer
    buffer_size_option = int(input(f'Digite a opção referente ao tamanho dos pacotes:'
                                   f'\n1. 500 bytes \n2. 1000 bytes \n3. 1500 bytes\n'))
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
    # client_socket.send(f"{filename_only}{SEPARATOR}{file_size}".encode())
    server_socket.sendto(filename_only, (SERVER_HOST, SERVER_PORT))
    # client_socket.sendall(amount_packages.to_bytes(4, "little"))
    # client_socket.sendall(BUFFER_SIZE[i].to_bytes(4, "little"))
    # check_sent = client_socket.recv(1024).decode()

    # start sending the file
    progress = tqdm.tqdm(range(file_size), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as file:
        bytes_read = file.read(BUFFER_SIZE[i])
        while (bytes_read):  # for j in range(amount_packages)

            if (server_socket.sendto(bytes_read, (SERVER_HOST, SERVER_PORT))):  # Se enviou le mais bytes
                bytes_read = file.read(BUFFER_SIZE[i])  # read the bytes from the file

            # update the progress bar
            progress.update(len(bytes_read))

    progress.close()
    # temp = client_socket.recv(4)
    # header = int.from_bytes(temp, "little")
    # client_socket.close()

    file.close()  # fecha o arquivo
    server_socket.close()

    end = time.time()
    total_time = end - start
    file_size_bit = file_size * 8

    speed = "{:,}".format(round(file_size_bit / total_time, 3)).replace('.', '/')
    speed = speed.replace(',', '.')
    speed = speed.replace('/', ',')

    print(f'\nTamanho do Arquivo Transmitido: {file_size} bytes')
    print(f'Número de Pacotes Enviados: {amount_packages}')
    print(f'Tempo de transmissão:  {round(total_time, 4)} s')
    print(f'Velocidade de Transmissão: {speed} bit/s')  # bit / s






