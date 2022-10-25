import socket
import logging
from collections import Counter
from time import sleep

IP_HOST = input("Enter the server host value:")  # Example: "191.52.64.78" -- The server's hostname or IP address
# PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
PORT = 8090
ADDRESS_SERVER = (IP_HOST, PORT)

# receive BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = 1500
HEADER_SIZE = 8
POSITION_SIZE = 4
SEPARATOR = '<split>'


def get_filename_and_size_and_amount_of_packages():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_tcp:
        # Using socket.SOCK_STREAM because the default protocol used is TCP
        # Using socket.AF_INET to use IPv4

        # Uses .connect() to connect to the server
        socket_tcp.connect(ADDRESS_SERVER)

        # Receiving file information
        filename, file_size = socket_tcp.recv(1024).decode("ISO-8859-1").split(SEPARATOR)

        sleep(0.000000000000000000000001)

        temp = socket_tcp.recv(4)
        amount_packages = int.from_bytes(temp, "little")

        global BUFFER_SIZE
        temp = socket_tcp.recv(4)
        BUFFER_SIZE = int.from_bytes(temp, "little")

        global HEADER_SIZE
        temp = socket_tcp.recv(4)
        HEADER_SIZE = int.from_bytes(temp, "little")
        print(f"info done\n\n")

        socket_tcp.close()
    return filename, file_size, amount_packages


def receive_packet(l_packages, file_bytes, index):
    print(f"receiving files")
    packet, ip = socket_udp.recvfrom(POSITION_SIZE + HEADER_SIZE + BUFFER_SIZE)
    print(f"received packet")
    position = int(packet[:POSITION_SIZE].decode())
    counter = int(packet[:HEADER_SIZE].decode('ISO-8859-1'))
    package = packet[HEADER_SIZE:]

    if counter == index:
        file_bytes[position] = package
    else:
        l_packages.append(index)
    return position, counter, package, l_packages, file_bytes


filename, file_size, amount_packages = get_filename_and_size_and_amount_of_packages()
print(f"filename={filename}\n\n"
      f"file_size={file_size}\n\n"
      f"amount_packages={amount_packages}\n\n")

# with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_udp:
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Using socket.DGRAM because the default protocol used is UDP
# Using socket.AF_INET to use IPv4
print(f"connecting\n\n")

header = []
files_list_of_bytes = []

j = 0

# while j < amount_packages:
while len(files_list_of_bytes) != amount_packages:
    lost_packages = []
    position, counter, package, lost_packages, files_list_of_bytes = receive_packet(lost_packages,
                                                                                    files_list_of_bytes, 1)
    position, counter, package, lost_packages, files_list_of_bytes = receive_packet(lost_packages,
                                                                                    files_list_of_bytes, 2)
    position, counter, package, lost_packages, files_list_of_bytes = receive_packet(lost_packages,
                                                                                    files_list_of_bytes, 3)
    position, counter, package, lost_packages, files_list_of_bytes = receive_packet(lost_packages,
                                                                                    files_list_of_bytes, 4)
    j += 1
    print(f"lost_packages={lost_packages}\n")
    socket_udp.sendto(lost_packages, IP_HOST)



with open(filename, "wb") as file:
    for i in range(amount_packages):
        file.write(files_list_of_bytes[i])


print(f'{filename} recebido.')

print(f'Encerrando conexão com o cliente')
socket_udp.close()

print(f'\nTamanho do Arquivo Transmitido: {file_size} bytes')
# print(f'Número de Pacotes Recebidos: {packages_received}')
# print(f'Número de Pacotes Perdidos: {packages_lost}')