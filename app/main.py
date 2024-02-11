# Uncomment this to pass the first stage
import asyncio 
import datetime
import argparse 
import struct

from app.config import RedisConfig 


SERVER_IP = "localhost"
SERVER_PORT = 6379
PING_RESPONSE = "+PONG\r\n"
NULL = "$-1\r\n"
database = {}
## database : {key :[value,"timer", "value", "datetime.now", "timer_value"] ]}

def encode_response(resp):
    if resp == NULL:
        return NULL
    return "+" + resp + "\r\n" 

def parse_arguements():
    parser = argparse.ArgumentParser(
            description = "Arguement Parser for redis implementation"
            )
    parser.add_argument("--dir", type=str, help="Directory to store RDB files")
    parser.add_argument("--dbfilename", type=str, help="The name of RDB file")
    return parser.parse_args()

def read_rdb_data(config):
    rdb_file_loc = config.dir + "/" + config.dbfilename
    with open(rdb_file_loc, "rb") as f:
        data = f.read()

    with open(rdb_file_loc, "rb") as f:
        while operand := f.read(1):
            print(operand)
            if operand == b"\xfb":
                break
        f.read(3)
        length = struct.unpack("B", f.read(1))[0]
        print("length")
        print(length)
        if length >> 6 == 0b00:
            length = length & 0b00111111
        else:
            length = 0
        val = f.read(length).decode()
        print(val)
        return val


async def handle_client(reader, writer): 
    ## parse arguements 
    args = parse_arguements()
    config = RedisConfig(dir = args.dir, dbfilename = args.dbfilename)
    print("The config is", config)

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

        if request[2].lower() == "keys":
            result = read_rdb_data(config)
            print("the result is", result)
            writer.write(f"*1\r\n${len(result)}\r\n{result}\r\n".encode())

        if request[2].lower() == "config":
            key = request[6].lower()
            if key == "dir":
                value = config.dir 
            else:
                value = config.dbfilename

            writer.write(f"*2\r\n${len(key)}\r\n{key}\r\n${len(value)}\r\n{value}\r\n".encode())

            
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
            exp_response = NULL

            if isinstance(value, tuple) and value[0] == "timer":
                time_difference = msg_time - value[2] 
                time_difference_in_ms = time_difference.total_seconds() * 1000
                if time_difference_in_ms >= float(value[3]):
                    del database[request[4]]
                else:
                    exp_response = value[1]
            else:
                exp_response = value
            value = encode_response(exp_response)
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
