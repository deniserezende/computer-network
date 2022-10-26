import logging
import socket
import os
import time
import select


class FileTransferUDP:
    def __init__(self):
        logging.info(f'__init__ of FileTransferUDP was called.')
        self.separator = '<split>'
        self.header_size = 8  # amount of bytes
        self.buffer_size = 1500
        self.is_sender = False
        self.filename = ''
        self.file_size = 0
        self.amount_of_packages = 0

        self.other_pc_ip = ""
        self.local_ip = ""
        self.other_pc_port = 8080
        self.local_port = 9090

        # Using socket.AF_INET to use IPv4
        # Using socket.STREAM because the default protocol used is TCP
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # Using socket.DGRAM because the default protocol used is UDP
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def begin(self):
        print("MENU")
        self.other_pc_ip = input('Enter the other computers ip: ')
        self.local_ip = input('Enter your ip: ')
        self.other_pc_port = int(input('Enter the other computers port: '))
        self.local_port = int(input('Enter your port: '))

        self.is_sender = bool(int(input(f'Enter an option: \n1. I\'m the receiver. \n2. I\'m the sender.\n')) - 1)
        logging.warning(f'the basic attributes of FileTransferUDP has been initialized')
        if self.is_sender:
            buffer_size_temp = int(input(f'Enter the package size: \n1. 1000 bytes\n2. 1500 bytes\n'))
            if buffer_size_temp == 1 or buffer_size_temp == 1000:
                self.buffer_size = 1000
            else:
                self.buffer_size = 1500

            self.filename = input('Enter the files name (including path): ')
            self.sender()
            logging.warning(f'Called the sender method')
        else:
            self.receiver()
            logging.info(f'Called the receiver method')

    def __s_connect_with_tcp__(self):
        # Connecting with the tcp
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_tcp.bind((self.local_ip, self.local_port))
        # The .listen() method enables a server to accept connections.
        self.socket_tcp.listen(1)
        # The .accept() method blocks execution and waits for an incoming connection.
        # When a client connects, it returns a new socket object representing the connection and a tuple holding
        # the address of the client.
        client_socket, address = self.socket_tcp.accept()
        logging.info(f'Connected via tcp')
        return client_socket

    def __s_send_basic_info_via_tcp__(self):
        client_socket = self.__s_connect_with_tcp__()
        filename_only = os.path.basename(self.filename)
        # client_socket.send(f"{filename_only}{self.separator}{self.file_size}".encode("ISO-8859-1"))
        client_socket.send(self.file_size.to_bytes(4, "little"))
        client_socket.send(self.amount_of_packages.to_bytes(4, "little"))
        client_socket.send(self.buffer_size.to_bytes(4, "little"))
        client_socket.send(self.header_size.to_bytes(4, "little"))
        client_socket.send(filename_only.encode("ISO-8859-1"))
        client_socket.close()
        logging.info(f'Basic info sent and connection closed')

    def __s_read_file__(self):
        file_list = [(None, None)] * self.amount_of_packages
        with open(self.filename, "rb") as file:
            # Creating a list of tuples with the bytes read and a counter from 1 to amount of packages
            for j in range(0, self.amount_of_packages):
                bytes_read = file.read(self.buffer_size)
                file_list[j] = (bytes_read, j)
        return file_list

    def __s_connect_with_udp__(self):
        # Connecting with the udp
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_udp.bind((self.local_ip, self.local_port))

        bytes_ = self.socket_udp.recvfrom(1024)
        message = bytes_[0]
        logging.warning(f'UDP bind check {message}')
        logging.warning(f'New address {bytes_[1]}')

    def __s_send_package__(self, package, index):
        actual_package = package[0]
        packet_identifier = package[1]
        logging.warning(f'sending package = (packet_identifier) = {packet_identifier}')

        # read the bytes from the file
        packet = (packet_identifier.to_bytes(4, "big") + index.to_bytes(4, "big") + actual_package)

        # we use sendall to assure transmission in
        # busy networks
        self.socket_udp.sendto(packet, (self.other_pc_ip, self.other_pc_port))

        logging.info(f'sending one package')

    def __s_send_packages__(self, file_list):
        finished = False
        # while list is not empty
        logging.info(f'Sending packages')
        lost_packages = [None, None, None, None]
        while file_list:
            logging.warning(f'len(file_list)={len(file_list)}')
            if len(file_list) < 4:
                end_range = len(file_list)
            else:
                end_range = 4
            for i in range(0, end_range):
                self.__s_send_package__(file_list[i], i)
                time.sleep(0.1)

            lost_packages_temp, ip = self.socket_udp.recvfrom(16)
            lost_packages.clear()
            lost_packages = [None, None, None, None]
            for i in range(0, end_range):
                lost_packages[i] = int.from_bytes(lost_packages_temp[i*4:i*4+4], "big")

            logging.warning(f'lost_packages={lost_packages}')
            for i in range(0, end_range):
                temp = file_list[i]
                logging.warning(f"file_list[{i}]={temp[1]}")
            # Removing the packages that have been sent from the list "to be sent"
            for p in range(0, end_range):
                logging.warning(f'lost_packages.count({p})={lost_packages.count(p)}')
                if lost_packages.count(p) == 0:
                    try:
                        package = file_list[0]
                        logging.warning(f'popping file[{0}] with id= {package[1]}')
                        file_list.pop(0) # tava p e tava errado, é 0?
                        logging.info(f'One more package successfully sent')
                    except:
                        if not file_list:
                            raise TypeError("List is empty")

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

        logging.info(f'Sender option selected')
        # Checking if the file exists
        if not os.path.exists(self.filename):
            logging.warning(f'Inserted file path doesn\'t exist {self.filename}')
            return

        # TCP - Sending basic info
        logging.info(f'Beginning the tcp connection to send basic info')
        # Getting the size of the file
        self.file_size = os.path.getsize(self.filename)
        # Setting the amount of packages
        self.amount_of_packages = (self.file_size // self.buffer_size) + 1
        # Connecting via tcp
        # Sending basic info: filename, size, amount of packages, buffer size, header size
        self.__s_send_basic_info_via_tcp__()
        # Closing connection
        self.socket_tcp.close()

        # File
        logging.info(f'Dealing with the file')
        file_list = self.__s_read_file__()

        # UDP - Sending file
        logging.info(f'Connecting with udp to begin sending the file')
        self.__s_connect_with_udp__()
        logging.info(f'Sending file by packages')
        self.__s_send_packages__(file_list)

        end = time.time()

        # Report overall performance
        self.__s_report_overall_performance__(start, end)

    def __r_connect_with_tcp__(self):
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Uses .connect() to connect to the server
        self.socket_tcp.connect((self.other_pc_ip, self.other_pc_port))

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
        logging.warning(f'Filename = {self.filename}')
        logging.warning(f'File size = {self.file_size}')
        logging.warning(f'Amount of packages = {self.amount_of_packages}')
        logging.warning(f'Buffer size = {self.buffer_size}')
        logging.warning(f'Header size = {self.header_size}')

    def __r_connect_with_udp__(self):
        # Connecting with the udp
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_udp.bind((self.local_ip, self.local_port))
        time.sleep(1)
        self.socket_udp.sendto("confirm".encode(), (self.other_pc_ip, self.other_pc_port))
        logging.warning(f'Trying to connect via UDP')
        time.sleep(1)

    def __r_receive_package__(self, position, file_list, lost_packages):
        last_one = False
        logging.info(f'Receiving a package')
        # 4 because it's the amount of bytes of an integer
        # that represents the index of each package
        packet, ip = self.socket_udp.recvfrom(4 + 4 + self.buffer_size)
        logging.warning(f'Received a package')

        packet_identifier = int.from_bytes(packet[:4], "big")
        index = int.from_bytes(packet[4:8], "big")
        package = packet[8:]
        logging.warning(f'packet_identifier={packet_identifier}')
        logging.warning(f'index={index}')

        file_list[packet_identifier] = package
        if index != position:
            lost_packages.append(position)

        # if position == index:
        #     file_list[packet_identifier] = package
        # else:
        #     lost_packages.append(index)
        if packet_identifier == self.amount_of_packages-1:
            last_one = True
        logging.warning(f'gonna return')
        return file_list, lost_packages, last_one

    def __r_receive_packages__(self):
        finished = False
        # while list is not empty
        logging.warning(f'Receiving packages')

        file_list = [None] * self.amount_of_packages
        # len(file_list) - file_list.count(None)
        lost_packages = []
        # AQUIDE while len(file_list) != self.amount_of_packages:
        while file_list.count(None) > 0:
            lost_packages.clear()
            if file_list.count(None) < 4:
                end_range = file_list.count(None)
            else:
                end_range = 4
            logging.warning(f'file_list.count(None)={file_list.count(None)}')
            logging.warning(f'end_range={end_range}')
            for i in range(0, end_range):
                logging.warning(f'Voltando no for')
                file_list, lost_packages, finished = self.__r_receive_package__(i, file_list, lost_packages)

            logging.warning(f"lost_packages={lost_packages}\n")

            lost_packages.append(7)
            lost_packages.append(7)
            lost_packages.append(7)
            lost_packages.append(7)

            packet = (lost_packages[0].to_bytes(4, "big") + lost_packages[1].to_bytes(4, "big") +
                      lost_packages[2].to_bytes(4, "big") + lost_packages[3].to_bytes(4, "big"))

            self.socket_udp.sendto(packet, (self.other_pc_ip, self.other_pc_port))

        return file_list

    def __r_write_file__(self, file_list):
        with open(self.filename, "wb") as file:
            for i in range(self.amount_of_packages):
                file.write(file_list[i])

        logging.warning(f'Finnished writting file')

    def __r_report_overall_performance__(self, start, end):
        total_time = end - start
        print(f'\nTamanho do Arquivo Transmitido: {self.file_size} bytes')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')

    def receiver(self):
        start = time.time()

        # TCP - Receiving basic info
        self.__r_receive_basic_info_via_tcp__()

        # UDP - Receiving file
        self.__r_connect_with_udp__()
        file_list = self.__r_receive_packages__()
        self.__r_write_file__(file_list)
        self.socket_udp.close()

        end = time.time()
        # Report overall performance
        self.__r_report_overall_performance__(start, end)
