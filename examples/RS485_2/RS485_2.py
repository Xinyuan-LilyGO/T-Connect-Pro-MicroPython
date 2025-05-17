from machine import UART, Pin
import time
import ustruct

# Pin definitions
RS485_TX_1 = 4
RS485_RX_1 = 5
RS485_TX_2 = 17
RS485_RX_2 = 18

# Constants
SERIAL_8N1 = 0x800001c

# Global variables
CycleTime = 0
Uart_Buf = bytearray(105)

RS485_1_Count = 0
RS485_2_Count = 0

Uart_Data = bytearray([
    0x0A,  # Device header
    
    # Dynamic data counter (4 bytes)
    0x00,  # High 2 bits
    0x00,  # High 1 bit
    0x00,  # Low 2 bits
    0x00,  # Low 1 bit
    
    # 100 data packets
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
    0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA
])

def uart_check_dynamic_data(uart_data, check_data):
    temp = ustruct.unpack('>I', uart_data[1:5])[0]
    return temp == check_data

def uart_check_static_data(uart_data):
    return uart_data[5:105] == Uart_Data[5:105]

def setup():
    print("Ciallo")
    
    # Initialize UARTs
    global uart1, uart2
    uart1 = UART(1, baudrate=115200, bits=8, parity=None, stop=1, tx=RS485_TX_1, rx=RS485_RX_1)
    uart2 = UART(2, baudrate=115200, bits=8, parity=None, stop=1, tx=RS485_TX_2, rx=RS485_RX_2)
    
    print("RS485 is preparing")
    for i in range(5, 0, -1):
        print(str(i))
        time.sleep(1)
    print("RS485 preparation completed")
    
    # Clear buffers
    while uart1.any():
        uart1.read(1)
    while uart2.any():
        uart2.read(1)

def loop():
    global RS485_1_Count, RS485_2_Count
    
    if Pin(0).value() == 0:
        time.sleep_ms(300)
        uart1.write(Uart_Data)
        uart2.write(Uart_Data)
        RS485_1_Count += 1
        RS485_2_Count += 1
    
    # Process UART1
    if uart1.any():
        time.sleep(1)  # Receive wait
        received = uart1.read()
        if received:
            Uart_Buf[:len(received)] = received
            
            if Uart_Buf[0] == 0x0A:
                if not uart_check_dynamic_data(Uart_Buf, RS485_1_Count):
                    while True:
                        print("[RS485_1] Check Dynamic Data Failed")
                        print("[RS485_1] Check Data:", RS485_1_Count)
                        received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                        print("[RS485_1] Received Data:", received_data)
                        for i in range(1, 5):
                            print("[RS485_1] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))
                        time.sleep(1)
                elif not uart_check_static_data(Uart_Buf):
                    print("[RS485_1] Check Static Data Failed")
                    for i in range(100):
                        print("[RS485_1] Received Buf[{}]: {:#X}".format(i+5, Uart_Buf[i+5]))
                    time.sleep(1)
                else:
                    time.sleep_ms(500)
                    print("[RS485_1] Check Data Successful")
                    print("[RS485_1] Check Data:", RS485_1_Count)
                    received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                    print("[RS485_1] Received Data:", received_data)
                    for i in range(1, 5):
                        print("[RS485_1] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))
                    print("[RS485_1] Received Buf[105]: {:#X}".format(Uart_Buf[104]))
                    
                    RS485_1_Count += 1
                    
                    # Update dynamic data
                    Uart_Data[1:5] = ustruct.pack('>I', RS485_1_Count)
                    
                    time.sleep(1)
                    uart1.write(Uart_Data)
                    
                    RS485_1_Count += 1
            else:
                time.sleep_ms(500)
                print("[RS485_1] Check Header Failed")
                print("[RS485_1] Received Header: {:#X}".format(Uart_Buf[0]))
                received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                print("[RS485_1] Received Data:", received_data)
                for i in range(1, 5):
                    print("[RS485_1] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))
    
    # Process UART2
    if uart2.any():
        time.sleep(1)  # Receive wait
        received = uart2.read()
        if received:
            Uart_Buf[:len(received)] = received
            
            if Uart_Buf[0] == 0x0A:
                if not uart_check_dynamic_data(Uart_Buf, RS485_2_Count):
                    while True:
                        print("[RS485_2] Check Dynamic Data Failed")
                        print("[RS485_2] Check Data:", RS485_2_Count)
                        received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                        print("[RS485_2] Received Data:", received_data)
                        for i in range(1, 5):
                            print("[RS485_2] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))
                        time.sleep(1)
                elif not uart_check_static_data(Uart_Buf):
                    print("[RS485_2] Check Static Data Failed")
                    for i in range(100):
                        print("[RS485_2] Received Buf[{}]: {:#X}".format(i+5, Uart_Buf[i+5]))
                    time.sleep(1)
                else:
                    time.sleep_ms(500)
                    print("[RS485_2] Check Data Successful")
                    print("[RS485_2] Check Data:", RS485_2_Count)
                    received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                    print("[RS485_2] Received Data:", received_data)
                    for i in range(1, 5):
                        print("[RS485_2] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))
                    print("[RS485_2] Received Buf[105]: {:#X}".format(Uart_Buf[104]))
                    
                    RS485_2_Count += 1
                    
                    # Update dynamic data
                    Uart_Data[1:5] = ustruct.pack('>I', RS485_2_Count)
                    
                    time.sleep(1)
                    uart2.write(Uart_Data)
                    
                    RS485_2_Count += 1
            else:
                time.sleep_ms(500)
                print("[RS485_2] Check Header Failed")
                print("[RS485_2] Received Header: {:#X}".format(Uart_Buf[0]))
                received_data = ustruct.unpack('>I', Uart_Buf[1:5])[0]
                print("[RS485_2] Received Data:", received_data)
                for i in range(1, 5):
                    print("[RS485_2] Received Buf[{}]: {:#X}".format(i, Uart_Buf[i]))

if __name__ == "__main__":
    # Main execution
    setup()
    while True:
        loop()