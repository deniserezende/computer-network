import socket
import os
import time

# PORT = int(input("Enter the server port value:"))  # Example: 5062 -- The port used by the server
PORT = 8090
IP_CLIENT = ""
ADDRESS_SERVER = ("", PORT)
ADDRESS_CLIENT = (IP_CLIENT, PORT)

SEPARATOR = '<split>'
# send BUFFER_SIZE[i] bytes each time
BUFFER_SIZE = [1000, 1500]
BUFFER_SIZE_CHOICE = 0
HEADER_SIZE = 8  # amount of bytes


def get_filename_and_size():
    # the name of file we want to send, make sure it exists
    # The filename needs to exist in the current directory,
    # or you can use an absolute path to that file somewhere on your computer.
    filename = input('Digite o nome do arquivo para enviar: ')

    # get the file size
    file_size = os.path.getsize(filename)

    return filename, file_size


def send_data_via_tcp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_tcp:
        # The .bind() method is used to associate the socket with a specific network interface and port number
        socket_tcp.bind(ADDRESS_SERVER)

        # The .listen() method enables a server to accept connections.
        socket_tcp.listen(1)

        # The .accept() method blocks execution and waits for an incoming connection.
        # When a client connects, it returns a new socket object representing the connection and a tuple holding
        # the address of the client.
        client_socket, addr = socket_tcp.accept()

        filename, file_size = get_filename_and_size()
        # print(f"file_size={file_size}\n\n")

        buffer_size_option = int(input(f'Digite a opção referente ao tamanho dos pacotes:'
                                       f'\n1. 1000 bytes \n2. 1500 bytes\n'))
        global BUFFER_SIZE_CHOICE
        if buffer_size_option == 1 or buffer_size_option == 1000:
            BUFFER_SIZE_CHOICE = 0
        elif buffer_size_option == 2 or buffer_size_option == 1500:
            BUFFER_SIZE_CHOICE = 1
        else:
            BUFFER_SIZE_CHOICE = 0

        # remove absolute path if there is
        filename_only = os.path.basename(filename)

        amount_packages = (file_size // BUFFER_SIZE[BUFFER_SIZE_CHOICE]) + 1

        client_socket.send(f"{filename_only}{SEPARATOR}{file_size}".encode("ISO-8859-1"))
        client_socket.send(amount_packages.to_bytes(4, "little"))
        client_socket.send(BUFFER_SIZE[BUFFER_SIZE_CHOICE].to_bytes(4, "little"))
        client_socket.send(HEADER_SIZE.to_bytes(4, "little"))

        client_socket.close()
        socket_tcp.close()
        return filename, file_size, amount_packages


def read_file(filename, amount):
    file_list = [(None, None)] * amount
    with open(filename, "rb") as file:
        for j in range(1, amount):
            temp = file.read(BUFFER_SIZE[BUFFER_SIZE_CHOICE])
            file_list[j] = (temp, j)
    return file_list


def send_package(package, index):
    actual_package = package[0]
    position = package[1]

    # Adding header
    header = str(index).zfill(HEADER_SIZE)
    header_id = bytes(header, 'ISO-8859-1')

    # read the bytes from the file
    packet = (bytes(position) + header_id + actual_package)

    # we use sendall to assure transmission in
    # busy networks
    socket_udp.sendto(packet, ADDRESS_CLIENT)


#MAIN


filename, file_size, amount_packages = send_data_via_tcp()

start = time.time()

# with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Using socket.DGRAM because the default protocol used is UDP
# Using socket.AF_INET to use IPv4

# The .bind() method is used to associate the socket with a specific network interface and port number
socket_udp.bind(ADDRESS_SERVER)
socket_udp.setblocking(False)
IP_CLIENT = input("Enter the client's IP address:")
ADDRESS_CLIENT = (IP_CLIENT, PORT)
# try:
#     socket_udp.connect(ADDRESS_CLIENT)
# except socket.timeout:
#     print('Tempo de limite para conexão UDP excedido.')
#     socket_udp.close()
#     exit(1)

#aqui
file_list = read_file(filename, amount_packages)

amount_of_lost_packages = 0
# for j in range(1, amount_packages, 4):
# parar esse for quando a lista estiver vazia
i = 0
while file_list and i < 10:
    i += 1
    lost_packages = []
    send_package(file_list[1], 1)
    time.sleep(0.000000000000000000000001)
    send_package(file_list[2], 2)
    time.sleep(0.000000000000000000000001)
    send_package(file_list[3], 3)
    time.sleep(0.000000000000000000000001)
    send_package(file_list[4], 4)

    lost_packages, ip = socket_udp.recvfrom(8)
    print(f"lost_packages={lost_packages}\n")
    print(f"lost_packages={lost_packages[0]}\n")
    print(f"lost_packages={lost_packages[1]}\n")
    print(f"lost_packages={lost_packages[2]}\n")
    print(f"lost_packages={lost_packages[3]}\n\n")

    amount_of_lost_packages = len(lost_packages)
    print(f"amount_of_lost_packages={amount_of_lost_packages}\n\n")

    for p in range(1, 4):
        if lost_packages.count(p) < 0:
            file_list.pop(p)

socket_udp.close()

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









