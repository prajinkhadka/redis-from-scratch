# Uncomment this to pass the first stage
# import socket
import socket

SERVER_IP = "localhost"
SERVER_PORT = 6379
PING_RESPONSE = "+PONG\r\n"

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server((SERVER_IP, SERVER_PORT), reuse_port = True)
    handle_connection(server_socket)

def handle_connection(server_socket):
    # Returns the clinet connection object and the client address. 

    client_connection, client_address = server_socket.accept()
    with client_connection:
        while True:
            print(f"Now connected to {client_address}") 
            data = client_connection.recv(1024).decode() 
            print("The data recieved is", data)

            print("The raw data is", data)
            # the data recieved for ping will be something like this : *1\r\n$4\r\nping\r\n 
            request = data.split("\r\n")
            print("The request recieved is", request)

            if 'ping' in request:
                client_connection.sendall(PING_RESPONSE.encode())

if __name__ == "__main__":
    main()
