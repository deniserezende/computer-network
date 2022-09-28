import socket

SERVER_HOST = input("Enter the server host value:") # Example: "191.52.64.78" -- The server's hostname or IP address
SERVER_PORT = int(input("Enter the server port value:")) # Example: 5062 -- The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_: 
    # Using socket.SOCK_STREAM because the default protocol used is TCP
    # Using socket.AF_INET to use IPv4
    
    # The .bind() method is used to associate the socket with a specific network interface and port number
    socket_.bind((SERVER_HOST, SERVER_PORT)) 
    
    # The .listen() method enables a server to accept connections.
    socket_.listen() 
    # The .listen() method has a backlog parameter. 
    # It specifies the number of unaccepted connections that the system will allow before refusing new connections. 
    # Starting in Python 3.5, it’s optional. If not specified, a default backlog value is chosen.

    # The .accept() method blocks execution and waits for an incoming connection. 
    # When a client connects, it returns a new socket object representing the connection and a tuple holding the address of the client.
    connection_socket, addr = socket_.accept()

    # One thing that’s imperative to understand is that you now have a new socket object from .accept(). 
    # This is important because it’s the socket that you’ll use to communicate with the client. 
    # It’s distinct from the listening socket that the server is using to accept new connections
    with connection_socket:
        print(f'Connected by {addr}')
        while True:
            data_received = connection_socket.recv(1024)
            if not data_received:
                break
            print(f"Mensagem recebida {data_received}")
            reply = input('Digite uma mensagem para enviar: ')
            reply_bytes = bytes(reply, 'utf-8')
            connection_socket.sendall(reply_bytes)
            
        print ('Encerrando conexão com o cliente')
        connection_socket.close()