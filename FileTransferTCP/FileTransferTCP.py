import logging
import socket
import os
import time

# TODO not working rever tudo
class FileTransferTCP:
    def __init__(self):
        logging.info(f'__init__ of FileTransferTCP was called.')
        self.separator = '<split>'
        self.header_size = 8  # amount of bytes
        self.buffer_size = 1500
        self.is_sender = False
        self.filename = ''
        self.file_size = 0
        self.amount_of_packages = 0

        self.host_ip = ""
        self.port = 8080

        # Using socket.AF_INET to use IPv4
        # Using socket.STREAM because the default protocol used is TCP
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.client_socket = None

    def begin(self):
        print("MENU")
        self.host_ip = input('Enter the host computers ip: ')
        self.port = int(input('Enter the port: '))

        self.is_sender = bool(int(input(f'Enter an option: \n1. I\'m the receiver. \n2. I\'m the sender.\n')) - 1)
        logging.info(f'the basic attributes of FileTransferUDP has been initialized')

        if self.is_sender:
            buffer_size_temp = int(input(f'Enter the package size: \n1. 500 bytes\n2. 1000 bytes\n3. 1500 bytes\n'))
            if buffer_size_temp == 1 or buffer_size_temp == 500:
                self.buffer_size = 500
            elif buffer_size_temp == 2 or buffer_size_temp == 1000:
                self.buffer_size = 1000
            else:
                self.buffer_size = 1500

            self.filename = input('Enter the files name (including path): ')
            self.sender()
            logging.warning(f'Called the sender method')
        else:
            self.receiver()
            logging.warning(f'Called the receiver method')

    def __s_connect_with_tcp__(self):
        # Connecting with the tcp
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_tcp.bind((self.host_ip, self.port))
        # The .listen() method enables a server to accept connections.
        self.socket_tcp.listen(1)
        # The .accept() method blocks execution and waits for an incoming connection.
        # When a client connects, it returns a new socket object representing the connection and a tuple holding
        # the address of the client.
        self.client_socket, address = self.socket_tcp.accept()
        logging.info(f'Connected via tcp')

    def __s_send_basic_info_via_tcp__(self):
        filename_only = os.path.basename(self.filename)
        # client_socket.send(f"{filename_only}{self.separator}{self.file_size}".encode("ISO-8859-1"))
        self.client_socket.send(self.file_size.to_bytes(4, "little"))
        self.client_socket.send(self.amount_of_packages.to_bytes(4, "little"))
        self.client_socket.send(self.buffer_size.to_bytes(4, "little"))
        self.client_socket.send(self.header_size.to_bytes(4, "little"))
        self.client_socket.send(filename_only.encode("ISO-8859-1"))
        logging.info(f'Basic info sent and connection closed')
        self.client_socket.close()

    def __s_read_file__(self):
        file_list = [(None, None)] * self.amount_of_packages
        with open(self.filename, "rb") as file:
            # Creating a list of tuples with the bytes read and a counter from 1 to amount of packages
            for j in range(0, self.amount_of_packages):
                bytes_read = file.read(self.buffer_size)
                file_list[j] = (bytes_read, j)
        return file_list

    def __s_send_package__(self, package, index):
        actual_package = package[0]
        packet_identifier = package[1]
        logging.info(f'sending package = (packet_identifier) = {packet_identifier}')

        # read the bytes from the file
        packet = (packet_identifier.to_bytes(4, "big") + index.to_bytes(4, "big") + actual_package)

        # we use sendall to assure transmission in busy networks
        self.client_socket.sendall(packet)

    def __s_send_packages__(self, file_list):
        logging.info(f'Sending packages')

        for i in range(0, len(file_list)):
            logging.info(f'len(file_list)={len(file_list)}')
            lost_package = self.amount_of_packages + 1
            while lost_package == i:
                self.__s_send_package__(file_list[i], i)
                lost_packages_temp = self.socket_udp.recv(4)
                lost_package = int.from_bytes(lost_packages_temp, "big")

        self.client_socket.close()

    def __s_report_overall_performance__(self, start, end):
        total_time = end - start
        file_size_bit = self.file_size * 8
        speed = "{:,}".format(round(file_size_bit / total_time, 3)).replace('.', '/')
        speed = speed.replace(',', '.')
        speed = speed.replace('/', ',')
        print(f'\nTamanho do Arquivo Transmitido: {self.file_size} bytes')
        print(f'Número de Pacotes Enviados: {self.amount_of_packages}')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')
        print(f'Velocidade de Transmissão: {speed} bit/s')  # bit / s

    def sender(self):
        start = time.time()
        # Checking if the file exists
        if not os.path.exists(self.filename):
            logging.warning(f'Inserted file path doesn\'t exist {self.filename}')
            return

        # TCP - Connecting
        logging.info(f'Beginning the tcp connection')
        # Getting the size of the file
        self.file_size = os.path.getsize(self.filename)
        # Setting the amount of packages
        self.amount_of_packages = (self.file_size // self.buffer_size) + 1
        # Connecting via tcp
        self.__s_connect_with_tcp__()
        self.__s_send_basic_info_via_tcp__()

        # File
        logging.info(f'Dealing with the file')
        file_list = self.__s_read_file__()

        # TCP - Sending file
        logging.info(f'Connecting with tcp to begin sending the file')
        self.__s_connect_with_tcp__()
        logging.info(f'Sending file by packages')
        self.__s_send_packages__(file_list)

        # Closing connection
        self.socket_tcp.close()

        end = time.time()

        # Report overall performance
        self.__s_report_overall_performance__(start, end)

    def __r_connect_with_tcp__(self):
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Uses .connect() to connect to the server
        self.socket_tcp.connect((self.host_ip, self.port))

    def __r_receive_basic_info_via_tcp__(self):
        self.__r_connect_with_tcp__()
        # Receiving file information
        # self.filename, self.file_size = self.socket_tcp.recv(1024).decode("ISO-8859-1").split(self.separator)

        temp = self.socket_tcp.recv(4)
        self.file_size = int.from_bytes(temp, "little")
        temp = self.socket_tcp.recv(4)
        self.amount_of_packages = int.from_bytes(temp, "little")
        temp = self.socket_tcp.recv(4)
        self.buffer_size = int.from_bytes(temp, "little")
        temp = self.socket_tcp.recv(4)
        self.header_size = int.from_bytes(temp, "little")
        temp = self.socket_tcp.recv(1024)
        self.filename = temp.decode("ISO-8859-1")

        self.socket_tcp.close()

        logging.info(f'Basic info received and connection closed')
        logging.info(f'Filename = {self.filename}')
        logging.info(f'File size = {self.file_size}')
        logging.info(f'Amount of packages = {self.amount_of_packages}')
        logging.info(f'Buffer size = {self.buffer_size}')
        logging.info(f'Header size = {self.header_size}')

    def __r_receive_package__(self, position, file_list, lost_packages):
        logging.info(f'Receiving a package')
        # 4 because it's the amount of bytes of an integer
        # that represents the index of each package
        packet = self.socket_tcp.recv(4 + 4 + self.buffer_size)
        logging.info(f'Received a package')

        packet_identifier = int.from_bytes(packet[:4], "big")
        index = int.from_bytes(packet[4:8], "big")
        package = packet[8:]
        logging.info(f'packet_identifier={packet_identifier}')
        logging.info(f'index={index}')

        file_list[packet_identifier] = package
        if index != position:
            lost_packages = position

        return file_list, lost_packages

    def __r_receive_packages__(self):
        logging.warning(f'Receiving packages')

        file_list = [None] * self.amount_of_packages
        lost_packages = self.amount_of_packages + 1
        i = 0
        while file_list.count(None) > 0:
            file_list, lost_packages = self.__r_receive_package__(i, file_list, lost_packages)

            packet = lost_packages.to_bytes(4, "big")
            self.socket_tcp.sendall(packet)
            i += 1

        return file_list

    def __r_write_file__(self, file_list):
        with open(self.filename, "wb") as file:
            for i in range(self.amount_of_packages):
                file.write(file_list[i])
        logging.info(f'Finnished writting file')

    def __r_report_overall_performance__(self, start, end):
        total_time = end - start
        print(f'\nTamanho do Arquivo Transmitido: {self.file_size} bytes')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')
        # print(f'Número de Pacotes Recebidos: {packages_received}')
        # print(f'Número de Pacotes Perdidos: {packages_lost}')

    def receiver(self):
        start = time.time()

        # TCP - Receiving basic info
        self.__r_receive_basic_info_via_tcp__()

        # UDP - Receiving file
        self.__r_connect_with_tcp__()
        file_list = self.__r_receive_packages__()
        self.__r_write_file__(file_list)
        self.socket_tcp.close()

        end = time.time()
        # Report overall performance
        self.__r_report_overall_performance__(start, end)



