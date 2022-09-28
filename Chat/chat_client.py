import socket

SERVER_HOST = input("Enter the server host value:") # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:")) # Example: 5062 -- The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_:
    # Using socket.SOCK_STREAM because the default protocol used is TCP
    # Using socket.AF_INET to use IPv4

    # Uses .connect() to connect to the server 
    socket_.connect((SERVER_HOST, SERVER_PORT))

    data = ""

    while True: 
        # Gets message input from the user and converts to bytes to send to the server
        message = input('Digite uma mensagem para enviar: ')
        message_bytes = bytes(message, 'utf-8')

        if message_bytes == "b'\x18'": # Control-x            
            break

        socket_.sendall(message_bytes)

        # Receives server reply
        data_received = socket_.recv(1024)
        print(f"Mensagem recebida {data_received}")

    socket_.close()
    

