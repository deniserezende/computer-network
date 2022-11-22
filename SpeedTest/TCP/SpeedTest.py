import logging
import socket
import os
import sys
import time


class SpeedTest:
    def __init__(self):
        logging.info(f'__init__ of SpeedTest was called.')
        self.separator = '<split>'
        self.header_size = 8  # amount of bytes
        self.is_sender = False
        self.file_size = 0
        self.data = 'teste de rede *2022*'
        self.amount_of_packages = 25
        self.buffer_size = self.data * self.amount_of_packages # 500 bytes

        self.local_ip = ""
        self.port_one = 8080
        self.port_two = 9090

        # Using socket.AF_INET to use IPv4
        # Using socket.STREAM because the default protocol used is TCP
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # Using socket.DGRAM because the default protocol used is UDP
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def begin(self):
        self.is_sender = bool(int(input(f'Enter an option: \n1. I\'m the receiver. \n2. I\'m the sender.\n')) - 1)
        logging.info(f'the basic attributes of SpeedTest has been initialized')

        if self.is_sender:
            self.sender()
            logging.warning(f'Called the sender method')
        else:
            self.receiver()
            logging.warning(f'Called the receiver method')

    def __s_connect_with_tcp__(self):
        # Connecting with the tcp
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_tcp.bind((self.local_ip, self.port_two))
        # The .listen() method enables a server to accept connections.
        self.socket_tcp.listen(1)
        # The .accept() method blocks execution and waits for an incoming connection.
        # When a client connects, it returns a new socket object representing the connection and a tuple holding
        # the address of the client.
        client_socket, address = self.socket_tcp.accept()
        logging.info(f'Connected via tcp')
        return client_socket

    def __s_create_list_of_data__(self):
        file_list = [(None, None)] * self.amount_of_packages
        # Creating a list of tuples with the bytes read and a counter from 1 to amount of packages
        for j in range(0, self.amount_of_packages):
            file_list[j] = (self.data, j)
        return file_list

    # def __s_connect_with_udp__(self):
    #     # Connecting with the udp
    #     self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    #
    #     # The .bind() method is used to associate the socket with a specific network interface and port number
    #     self.socket_udp.bind((self.local_ip, self.port_two))
    #
    #     bytes_ = self.socket_udp.recvfrom(1024)
    #     message = bytes_[0]

    def __s_send_package__(self, package, index):
        actual_package = package[0]
        packet_identifier = package[1]
        logging.info(f'sending package = (packet_identifier) = {packet_identifier}')

        # read the bytes from the file
        packet = (packet_identifier.to_bytes(4, "big") + index.to_bytes(4, "big") + actual_package)

        # we use sendall to assure transmission in
        # busy networks
        # self.socket_udp.sendto(packet, (self.other_pc_ip, self.port_one))
        self.socket_tcp.sendall(packet)

    def __s_send_packages__(self, file_list):
        # while list is not empty
        logging.info(f'Sending packages')
        lost_packages = [None, None, None, None]

        begin_time = time.time()
        running_time = 0

        while running_time <= 20:
            if len(file_list) < 4:
                end_range = len(file_list)
            else:
                end_range = 4
            for i in range(0, end_range):
                self.__s_send_package__(file_list[i], i)
                time.sleep(0.1)

            # lost_packages_temp, ip = self.socket_udp.recvfrom(16)
            lost_packages_temp = self.socket_tcp.recv(16)
            lost_packages.clear()
            lost_packages = [None, None, None, None]
            for i in range(0, end_range):
                lost_packages[i] = int.from_bytes(lost_packages_temp[i * 4:i * 4 + 4], "big")

            # Removing the packages that have been sent from the list "to be sent"
            for p in range(0, end_range):
                if lost_packages.count(p) == 0:
                    try:
                        file_list.pop(0)
                        logging.info(f'One more package successfully sent')
                    except:
                        if not file_list:
                            raise TypeError("List is empty")
            current = time.time()
            running_time = begin_time - current

    def __s_report_overall_performance__(self, start, end):
        total_time = end - start
        file_size_bit = self.file_size * 8
        speed = "{:,}".format(round(file_size_bit / total_time, 3)).replace('.', '/')
        speed = speed.replace(',', '.')
        speed = speed.replace('/', ',')
        print(f'Número de Pacotes Enviados: {self.amount_of_packages}')
        print(f'Bytes Enviados: {self.buffer_size}')
        print(f'Velocidade de Transmissão: {speed} bit/s')  # bit / s

    def sender(self):
        # Checking if the file exists
        if not os.path.exists(self.filename):
            logging.warning(f'Inserted file path doesn\'t exist {self.filename}')
            return

        start = time.time()

        logging.info(f'Connecting with tcp to begin sending data')
        self.__s_connect_with_tcp__()
        logging.info(f'Sending file by packages')
        file_list = self.__s_create_list_of_data__()
        self.__s_send_packages__(file_list)
        # Closing connection
        self.socket_tcp.close()

        end = time.time()

        # Report overall performance
        self.__s_report_overall_performance__(start, end)

    def __r_connect_with_tcp__(self):
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Uses .connect() to connect to the server
        self.socket_tcp.connect((self.other_pc_ip, self.port_one))

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

    def __r_connect_with_udp__(self):
        # Connecting with the udp
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_udp.bind((self.local_ip, self.port_two))
        time.sleep(1)
        self.socket_udp.sendto("confirm".encode(), (self.other_pc_ip, self.port_one))
        time.sleep(1)
        logging.info(f'Trying to connect via UDP')

    def __r_receive_package__(self, position, file_list, lost_packages):
        logging.info(f'Receiving a package')
        # 4 because it's the amount of bytes of an integer
        # that represents the index of each package
        # packet, ip = self.socket_udp.recvfrom(4 + 4 + self.buffer_size)
        packet = self.socket_tcp.recv(4 + 4 + self.buffer_size)

        logging.info(f'Received a package')

        packet_identifier = int.from_bytes(packet[:4], "big")
        index = int.from_bytes(packet[4:8], "big")
        package = packet[8:]
        logging.info(f'packet_identifier={packet_identifier}')
        logging.info(f'index={index}')

        file_list[packet_identifier] = package
        if index != position:
            lost_packages.append(position)

        return file_list, lost_packages

    def __r_receive_packages__(self):
        logging.info(f'Receiving packages')
        file_list = [None] * self.amount_of_packages
        lost_packages = []

        while file_list.count(None) > 0:
            lost_packages.clear()
            if file_list.count(None) < 4:
                end_range = file_list.count(None)
            else:
                end_range = 4
            for i in range(0, end_range):
                file_list, lost_packages = self.__r_receive_package__(i, file_list, lost_packages)

            logging.warning(f"lost_packages={lost_packages}\n")

            lost_packages.append(7)
            lost_packages.append(7)
            lost_packages.append(7)
            lost_packages.append(7)

            packet = (lost_packages[0].to_bytes(4, "big") + lost_packages[1].to_bytes(4, "big") +
                      lost_packages[2].to_bytes(4, "big") + lost_packages[3].to_bytes(4, "big"))

            # self.socket_udp.sendto(packet, (self.other_pc_ip, self.port_one))
            self.socket_tcp.sendall(packet)

        return file_list

    def __r_write_file__(self, file_list):
        with open(self.filename, "wb") as file:
            for i in range(self.amount_of_packages):
                file.write(file_list[i])
        logging.info(f'Finnished writting file')

    def __r_report_overall_performance__(self, start, end, lost_packages):
        total_time = end - start
        received_packages = self.amount_of_packages - lost_packages
        print(f'Número de Pacotes Recebidos: {received_packages}')
        print(f'Número de Pacotes Perdidos: {lost_packages}')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')

    def receiver(self):
        start = time.time()

        # TCP - Receiving file
        self.__r_connect_with_tcp__()
        file_list = self.__r_receive_packages__()
        self.socket_tcp.close()

        end = time.time()
        amount_lost_packages = file_list.count(None)
        # Report overall performance
        self.__r_report_overall_performance__(start, end, amount_lost_packages)
