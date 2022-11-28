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
        self.test = 'teste de rede *2022*'
        self.buffer_size = 500
        self.data = self.test * int(self.buffer_size / len(self.test))
        self.amount_of_packages = 25000000
        self.lost_packages = 0
        self.sent_packages = 0
        self.received_packages = 0

        self.local_ip = ""
        self.port_one = 9090
        self.other_ip = ""

        # Using socket.AF_INET to use IPv4
        # Using socket.STREAM because the default protocol used is TCP
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.client_socket = None

    def begin(self):
        # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.is_sender = bool(int(input(f'Enter an option: \n1. I\'m the receiver. \n2. I\'m the sender.\n')) - 1)
        logging.info(f'the basic attributes of SpeedTest has been initialized')

        if self.is_sender:
            self.other_ip = input("Other pc ip: ")
            self.sender()
            logging.warning(f'Called the sender method')
        else:
            self.local_ip = input("Server ip: ")
            self.receiver()
            logging.warning(f'Called the receiver method')

    def __s_connect_with_tcp__(self):
        # Connecting with the tcp
        self.socket_tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_tcp.bind((self.local_ip, self.port_one))
        # The .listen() method enables a server to accept connections.
        self.socket_tcp.listen(1)
        # The .accept() method blocks execution and waits for an incoming connection.
        # When a client connects, it returns a new socket object representing the connection and a tuple holding
        # the address of the client.
        self.client_socket, address = self.socket_tcp.accept()
        logging.info(f'Connected via tcp')

    def __s_create_list_of_data__(self):
        file_list = [(None, None)] * self.amount_of_packages
        # Creating a list of tuples with the bytes read and a counter from 1 to amount of packages
        for j in range(0, self.amount_of_packages):
            file_list[j] = (self.data, j)
        return file_list

    def __s_send_package__(self, package, index):
        actual_package = package[0]
        packet_identifier = package[1]
        logging.info(f'sending package = (packet_identifier) = {packet_identifier}')

        # read the bytes from the file
        packet = (packet_identifier.to_bytes(4, "big") + index.to_bytes(4, "big") + actual_package.encode('utf-8'))

        # we use sendall to assure transmission in
        # busy networks
        try:
            self.client_socket.sendall(packet)
            self.sent_packages += 1
        except BrokenPipeError:
            logging.error(f"Broken pipe")
        except AttributeError:
            logging.error(f"'NoneType' object has no attribute 'sendall'\nConnection closed.")

    def __s_send_packages__(self, file_list):
        # while list is not empty
        logging.info(f'Sending packages')

        begin_time = time.time()
        running_time = 0

        i = 0
        while running_time <= 20:
            self.__s_send_package__(file_list[i], i)
            i += 1
            try:
                lost_packages_temp = int.from_bytes(self.client_socket.recv(4), "big")
                if lost_packages_temp == 1:
                    self.lost_packages += 1
            except ConnectionResetError:
                logging.error(f"Connection reset by peer")
                self.sent_packages -= 1
                break
            except AttributeError:
                logging.error(f"'NoneType' object has no attribute 'sendall'\nConnection closed.")

            current = time.time()
            running_time = current - begin_time
            logging.info(f'running_time={running_time}')

    def __s_report_overall_performance__(self, start, end):
        total_time = end - start
        size_bit = self.buffer_size * self.sent_packages * 8  # bits
        speed_value = round(size_bit / total_time, 3)
        speed = "{:,}".format(speed_value).replace('.', '/')
        speed = speed.replace(',', '.')
        speed = speed.replace('/', ',')
        print(f'Número de Pacotes Enviados: {self.sent_packages}')
        print(f'Bytes Enviados: {self.sent_packages * self.buffer_size}')
        print(f'Tempo de Transmissão: {total_time} s')  # bit / s
        print(f'Velocidade de Transmissão: {speed} bit/s')  # bit / s
        print(f'Velocidade de Transmissão: {round(speed_value / 1000000, 3)} Mbps')  # bit / s

    def sender(self):
        start = time.time()

        logging.info(f'Connecting with tcp to begin sending data')
        self.__s_connect_with_tcp__()
        logging.info(f'Sending file by packages')
        file_list = self.__s_create_list_of_data__()
        self.__s_send_packages__(file_list)
        logging.info(f'Receiving file by packages')
        self.socket_tcp.close()
        end = time.time()

        # Report overall performance
        self.__s_report_overall_performance__(start, end)

        time.sleep(1)

        start = time.time()
        self.local_ip = self.other_ip  # Acho
        self.__r_connect_with_tcp__()
        self.__r_receive_packages__()
        # Closing connection
        self.socket_tcp.close()

        end = time.time()

        # Report overall performance
        self.__r_report_overall_performance__(start, end)

    def __r_connect_with_tcp__(self):
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Uses .connect() to connect to the server
        self.socket_tcp.connect((self.local_ip, self.port_one))

    def __r_receive_package__(self, position, file_list):
        logging.info(f'Receiving a package')
        # 4 because it's the amount of bytes of an integer
        # that represents the index of each package
        try:
            packet = self.socket_tcp.recv(4 + 4 + self.buffer_size)
            logging.info(f'Received a package')
            packet_identifier = int.from_bytes(packet[:4], "big")
            index = int.from_bytes(packet[4:8], "big")
            package = packet[8:]
            logging.info(f'packet_identifier={packet_identifier}')
            logging.info(f'index={index}')

            file_list[packet_identifier] = package
            if index != position:
                self.lost_packages += 1
                return file_list, 1
            self.received_packages += 1
            return file_list, 0

        except:
            logging.error("")
            return file_list, 1

    def __r_receive_packages__(self):
        logging.info(f'Receiving packages')
        file_list = [None] * self.amount_of_packages

        begin_time = time.time()
        running_time = 0

        i = 0
        while running_time <= 20:
            file_list, lost_package = self.__r_receive_package__(i, file_list)
            i += 1

            packet = (lost_package.to_bytes(4, "big"))
            try:
                self.socket_tcp.sendall(packet)
            except OSError:
                logging.error(f'[Errno 57] Socket is not connected')

            current = time.time()
            running_time = current - begin_time
            logging.info(f'running_time={running_time}')

        return file_list

    def __r_report_overall_performance__(self, start, end):
        total_time = end - start
        print(f'Número de Pacotes Recebidos: {self.received_packages}')
        print(f'Número de Pacotes Perdidos: {self.lost_packages}')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')

    def receiver(self):
        start = time.time()

        # TCP - Receiving file
        self.__r_connect_with_tcp__()
        logging.info(f'Receiving file by packages')
        self.__r_receive_packages__()
        logging.info(f'Sending file by packages')
        self.socket_tcp.close()

        end = time.time()
        # Report overall performance
        self.__r_report_overall_performance__(start, end)
        time.sleep(1)

        start = time.time()
        self.local_ip = self.other_ip  # Acho
        self.__s_connect_with_tcp__()
        file_list = self.__s_create_list_of_data__()
        self.__s_send_packages__(file_list)
        self.socket_tcp.close()

        end = time.time()
        # Report overall performance
        self.__s_report_overall_performance__(start, end)
