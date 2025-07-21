import asyncio, serial_asyncio



class SerialProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.rxBuffer = bytearray()
        print("Serial port opened", transport)


    def data_received(self, data):
        # called whenever bytes arrive
        self.rxBuffer.extend(data)
        if(self.rxBuffer.find(b'!') != -1): #packet finished
            print("Received:  ", self.rxBuffer.decode('utf-8') )
            self.rxBuffer.clear()


    def send(self, data):
        if self.transport:
            self.transport.write(data.encode('utf-8'))
            print(f"Sent: {data!r}")
        else:
            print("Transport not ready :(")


    def connection_lost(self, exc):
        print("Serial port closed")
        asyncio.get_event_loop().stop()



class Tester:
    def __init__(self, proto):
        self.proto = proto

    def test_LED(self):
        self.proto.send("LED!")
    
    def test_sensors(self, params):
        self.proto.send(f"SENSORS,{params[0]},{params[1]},{params[2]},{params[3]}!")

    def test_boot(self):
        self.proto.send("BOOT!")

    def test_ping(self):
        self.proto.send("PING!")



async def test_commands(tester):
    loop = asyncio.get_running_loop()
    while 1:
        user_input = await loop.run_in_executor(None, input, "+++ Enter test command:\n")
        if user_input == 'led':
            tester.test_LED()
        elif user_input == 'boot':
            tester.test_boot()
        elif user_input == 'ping':
            tester.test_ping()
        elif user_input == 'sensors':
            tester.test_sensors([1, 2, 3, 4])
        else:
            print("Test command not found! ")


async def main():
    # adjust port and baudrate
    _, proto = await serial_asyncio.create_serial_connection(asyncio.get_running_loop(), SerialProtocol, 'COM9', baudrate=9600)

    tester = Tester(proto) 
    asyncio.create_task(test_commands(tester))
    
    await asyncio.Event().wait()  # This never finishes
    # the loop will call data_received asynchronously


if __name__ == "__main__":
    print("Begin! :)")
    asyncio.run(main())



    
