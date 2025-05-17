import time
from machine import UART, Pin

RS485_TX_1 = 4
RS485_RX_1 = 5
RS485_TX_2 = 17
RS485_RX_2 = 18

uart1 = UART(1, baudrate=115200, tx=Pin(RS485_TX_1), rx=Pin(RS485_RX_1))
uart2 = UART(2, baudrate=115200, tx=Pin(RS485_TX_2), rx=Pin(RS485_RX_2))

temp = 0
cycle_time = 0

def setup():
    print("Ciallo")
    print("RS485 is preparing")

    time.sleep(1)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)
    print("RS485 preparation completed")

    while uart1.any():
        uart1.read()
    while uart2.any():
        uart2.read()

def loop():
    global temp, cycle_time
    while True:
        if time.ticks_ms() > cycle_time:
            temp += 1
            uart1.write(f"{temp}\n")
            time.sleep(0.01) 
            uart2.write(f"{temp}\n")
            cycle_time = time.ticks_ms() + 3000

        if uart1.any():
            data = uart1.read()
            if data:
                decoded_data = data.decode('utf-8').strip()
                if decoded_data:
                    print("RS485_1 receive data: {}".format(decoded_data))

        if uart2.any():
            data = uart2.read()
            if data:
                decoded_data = data.decode('utf-8').strip()
                if decoded_data: 
                    print("RS485_2 receive data: {}".format(decoded_data))

if __name__ == "__main__":
    setup()
    loop()