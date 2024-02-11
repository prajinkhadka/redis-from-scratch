# Uncomment this to pass the first stage
import asyncio 

SERVER_IP = "localhost"
SERVER_PORT = 6379
PING_RESPONSE = "+PONG\r\n"

async def handle_client(reader, writer):
    # need to write on the client 
    client_address = writer.get_extra_info("peername") 
    print(f"Connected to the client with IP {client_address}")
    # we might recivie multiple request from the same client so to handle that run a loopj
    while True:
        # read the data from client
        data = await reader.read(1024)
        if not data:
            break 
        message = data.decode() 
        request = message.split("\r\n")
        print("The request for echo is", request)

        if request[2] == "echo":
            response_value  = request[4]
            print("The response_value is", response_value)
            await writer.write(response_value.encode())

        if "ping" in request:
            writer.write(PING_RESPONSE.encode())
            await writer.drain() 

        # writer.close()


async def main():
    # Using asyncio to handle non blocking call
    server = await asyncio.start_server(handle_client, SERVER_IP, SERVER_PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
