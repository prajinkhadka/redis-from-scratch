# Uncomment this to pass the first stage
import asyncio 
import datetime

SERVER_IP = "localhost"
SERVER_PORT = 6379
PING_RESPONSE = "+PONG\r\n"
NULL = "$-1\r\n"
database = {}
## database : {key :[value,"timer", "value", "datetime.now", "timer_value"] ]}

def encode_response(resp):
    return "+" + resp + "\r\n" 

async def handle_client(reader, writer):
    # need to write on the client 
    client_address = writer.get_extra_info("peername") 
    print(f"Connected to the client with IP {client_address}")
    # we might recivie multiple request from the same client so to handle that run a loopj
    while True:
        # read the data from client
        data = await reader.read(1024)
        msg_time = datetime.datetime.now()

        if not data:
            break 
        message = data.decode() 
        request = message.split("\r\n")
        print("The request for get set is", request)

        if request[2].lower() == "set":
            key, value = request[4], request[6]
            if "px" in request:
                timer = request[10]
                database[key] = ("timer", value, datetime.datetime.now(), timer)
            else:
                database[key] = value
            resp = "OK"
            response_value = encode_response(resp)
            writer.write(response_value.encode()) 

        if request[2].lower() == "get":
            value = database.get(request[4], "$-1\r\n") 
            print("the value getted is", value)

            if isinstance(value, tuple):
                print("the value of 2 is", value[2])
                time_difference = msg_time - value[2] 
                time_difference_in_ms = time_difference.total_seconds() * 1000
                print("the time_difference_in_ms is", time_difference_in_ms)

                print("the value of 3 is", value[3])
                if time_difference_in_ms >= float(value[3]):
                    del database[request[4]]
                else:
                    value = value[1]

            else:
                value = value
            print("the value is", value) 
            value = encode_response(value)
            writer.write(value.encode())
            
        if request[2].lower() == "echo":
            response_value = encode_response(request[4])
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
