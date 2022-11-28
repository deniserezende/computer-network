import logging
import socket
import os
import time


class SpeedTest:
    def __init__(self):
        logging.info(f'__init__ of SpeedTest was called.')
        self.is_sender = False
        self.amount_of_packages = 25
        self.amount_of_lostpackages = 0
        self.amount_received_packgs = 0
        self.sent_packages = 0
        self.counter = 0
        self.test = 'teste de rede *2022*'
        self.buffer_size = 500
        self.data = self.test * int(self.buffer_size / len(self.test))

        self.other_pc_ip = ""
        self.local_ip = ""
        self.other_pc_port = 8080
        self.local_port = 9090

        # Using socket.DGRAM because the default protocol used is UDP
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def begin(self):
        print("MENU")
        self.other_pc_ip = input('Enter the other computers ip: ')
        self.local_ip = input('Enter your ip: ')
        self.other_pc_port = int(input('Enter the other computers port: '))
        self.local_port = int(input('Enter your port: '))

        self.is_sender = bool(int(input(f'Enter an option: \n1. I\'m the receiver. \n2. I\'m the sender.\n')) - 1)
        logging.info(f'the basic attributes of SpeedTest has been initialized')

        if self.is_sender:
            self.sender()
            logging.warning(f'Called the sender method')
        else:
            self.receiver()
            logging.warning(f'Called the receiver method')

    def __s_connect_with_udp__(self):
        # Connecting with the udp
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # The .bind() method is used to associate the socket with a specific network interface and port number
        self.socket_udp.bind((self.local_ip, self.local_port))

        bytes_ = self.socket_udp.recvfrom(1024)
        message = bytes_[0]

    def __s_send_package__(self, string):
        logging.info(f'sending strings!')
        try:
            self.socket_udp.sendto(string.encode(), (self.other_pc_ip, self.other_pc_port))
            self.sent_packages += 1
        except BrokenPipeError:
            logging.error(f"Broken pipe")

    def __s_send_packages__(self):
        logging.info(f'Sending packages')
        begin_time = time.time()
        running_time = 0

        while running_time <= 20:
            self.__s_send_package__(self.data)
            #time.sleep(0.001)

            current_time = time.time()
            running_time = current_time - begin_time

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
        print(f'Velocidade de Transmissão: {round(speed_value/1000000, 3)} Mbps')  # bit / s

    def sender(self):
        start = time.time()

        # UDP - Sending string
        logging.info(f'Connecting with udp to begin sending the data')
        self.__s_connect_with_udp__()
        logging.info(f'Sending data')
        self.__s_send_packages__()
        self.socket_udp.close()
        self.__r_connect_with_udp__()
        self.__r_receive_packages__()
        self.socket_udp.close()

        end = time.time()

        # Report overall performance
        self.__s_report_overall_performance__(start, end)

    def __r_connect_with_udp__(self):
        # Connecting with the udp
        self.socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_udp.bind((self.local_ip, self.local_port))
        #time.sleep(1)
        self.socket_udp.sendto("confirm".encode(), (self.other_pc_ip, self.other_pc_port))
        #time.sleep(1)
        logging.info(f'Trying to connect via UDP')

    def __r_receive_package__(self):
        logging.info(f'Receiving a package')
        # 4 because it's the amount of bytes of an integer
        # that represents the index of each package
        string, ip = self.socket_udp.recvfrom(4 + 4 + self.buffer_size)
        if(string == ""):
            self.counter+=1
        else:
            self.amount_received_packgs+=1

        return string

    def __r_receive_packages__(self):
        logging.info(f'Receiving data')
        begin_time = time.time()
        running_time = 0
        while running_time <= 20:
            string = self.__r_receive_package__()
            #time.sleep(0.001)

            current_time = time.time()
            running_time = current_time - begin_time
        
        return string

    def __r_report_overall_performance__(self, start, end, lost_packages, received_packages):
        total_time = end - start
        #TODO arrumar relatorios
        print(f'Número de Pacotes Recebidos: {received_packages}')
        print(f'Número de Pacotes Perdidos: {lost_packages}')
        print(f'Tempo de transmissão:  {round(total_time, 4)} s')

    def receiver(self):
        start = time.time()

        # UDP - Receiving string
        self.__r_connect_with_udp__()
        string = self.__r_receive_packages__()
        self.socket_udp.close()
        self.__s_connect_with_udp__()
        self.__s_send_packages__()
        self.socket_udp.close()

        end = time.time()
        amount_lost_packages = self.counter
        amount_received_packages = self.amount_received_packgs - amount_lost_packages
        # Report overall performance
        self.__r_report_overall_performance__(start, end, amount_lost_packages, amount_received_packages)
