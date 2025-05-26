from sx1262 import SX1262
import st7796
import time
import machine
import network
import CST226SE

touch_sensor = CST226SE.CST226SE(39, 40, 47, 3)  # SDA, SCL, RST, INT pin numbers  
while not touch_sensor.begin_touch_sensor():
    time.sleep(2)
print("CST226SE initialization successfully")

# Initialize global variables
operation_done = False
transmit_flag = False
transmission_state = None
Connecting_mac = None
send_mac = None
send_data = 0
receive_data = 0
error_count = 0

# Define connection states
UNCONNECTED = 0
CONNECTING = 1
CONNECTED = 2
connection_flag = UNCONNECTED  # Initialize connection flag
current_connection_flag = 0
previous_connection_flag = 0

# Callback function definition
def cb(events):
    global operation_done, transmit_flag, connection_flag, receive_data, last_receive_time, Connecting_mac
    if events & SX1262.RX_DONE:  # Check if RX_DONE event occurred
        msg, err = sx.recv()  # Receive the message
        error = SX1262.STATUS.get(err, "Unknown error")
        
        try:
            msg_str = msg.decode('utf-8')
            if msg_str.startswith("MAC:"): 
                Connecting_mac = msg_str[4:]
                print("[SX1262] Received MAC Address:", Connecting_mac)
                time.sleep(0.1)
            else:
                receive_data = int(msg_str)
                if receive_data == 1 :
                    send_mac = f"MAC:{get_mac_address()}"
                    sx.send(str(send_mac).encode('utf-8'))
                    print(send_mac)
                    time.sleep(0.1)
                
        except ValueError:
            receive_data = 0  

        # Update connection status to CONNECTED
        connection_flag = CONNECTED  # Mark as connected
        operation_done = True
        transmit_flag = False
        
    elif events & SX1262.TX_DONE:
        print("[SX1262] Transmission finished!")
        last_receive_time = time.ticks_ms()  # 刷新接收时间戳
        operation_done = True
        transmit_flag = True
        if connection_flag == UNCONNECTED:
            connection_flag = CONNECTING  # 只在未连接时，尝试标记为连接中

def get_mac_address():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True) 
    mac = wlan.config('mac')
    formatted_mac = ''
    for x in mac:
        hex_str = hex(x)[2:].upper() 
        if len(hex_str) == 1:
            hex_str = '0' + hex_str
        formatted_mac += hex_str
    return formatted_mac

local_mac = get_mac_address()

# Initialize SX1262 instance with ESP32S3 pin configuration
sx = SX1262(spi_bus=1, clk=12, mosi=11, miso=13, cs=14, irq=45, rst=42, gpio=38)
freq = 868.6
bw = 125.0
power = 22
# LoRa mode configuration
sx.begin(freq=freq, bw=bw, sf=12, cr=8, syncWord=0x12,
         power=power, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True)

# Set the callback function
sx.setBlockingCallback(False, cb)

initiating_node = True  # Set True for the initiating node, False for the responding node

def setup():
#     st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    print("[SX1262] Initializing ... ")
    if initiating_node:
        print("[SX1262] Sending first packet with data: {}".format(send_data))
        transmission_state = sx.send(str(send_data).encode())
        
        if isinstance(transmission_state, tuple):
            if transmission_state[0] == 0:
                print("[SX1262] Transmission finished!")
            else:
                print(f"[SX1262] Failed, code {transmission_state[0]}")
        else:
            print("[SX1262] Unexpected TX state format")
        
        transmit_flag = True
    else:
        print("[SX1262] Starting to listen ... ")
        state = sx.startReceive()
        print("RX state: {}".format(SX1262.STATUS.get(state, "Unknown error")))
        
    
# Call the setup function to initialize the radio
setup()
shared_spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))
st7796_display = st7796.ST7796(spi=shared_spi, cs=21, dc=41, rst=47, bl=46)
st7796_display.fillScreen(0, 0, st7796_display.WHITE)
st7796_display.draw_text(100, 100, "TEST", st7796_display.PALERED, st7796_display.WHITE, size=4, rotation=1)
st7796_display.draw_text(60, 145, "SX1262 callback distance test", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
st7796_display.draw_text(140, 200, "3", st7796_display.RED, st7796_display.WHITE, size=4, rotation=1)
time.sleep(1)
st7796_display.draw_text(140, 200, "2", st7796_display.RED, st7796_display.WHITE, size=4, rotation=1)
time.sleep(1)
st7796_display.draw_text(140, 200, "1", st7796_display.RED, st7796_display.WHITE, size=4, rotation=1)
time.sleep(1)
st7796_display.fillScreen(0, 0, st7796_display.WHITE)
previous_connection_flag = None
last_receive_time = time.ticks_ms()
# Main loop
while True:
    if touch_sensor.is_touch_detected():
        touch_sensor.clear_touch_interrupt_flag()
        finger_number, touches, pressures = touch_sensor.read_touch_data()
        for i, (x, y) in enumerate(touches, start=1):
            print(f"Touch X{i}:{x} Y{i}:{y}")
            if (100<x<120 and 230<y<300):
                connection_flag = CONNECTING

    if operation_done:
        operation_done = False
        if transmit_flag:
            # After transmission, start receiving
            sx.startReceive()
            transmit_flag = False
        else:
            # Increment the data and send
            send_data += 1
            print("[SX1262] Sending updated packet with data: {}".format(send_data))
            transmission_state = sx.send(str(send_data).encode())
            transmit_flag = True
            
    if connection_flag == UNCONNECTED or connection_flag == CONNECTING:
        current_connection_flag = 0
        st7796_display.draw_text(75, 40, "SX1262 Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=1)
        st7796_display.draw_text(75, 80, "[Status]:Init successful", st7796_display.GREEN, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 90, "[Mode]:LoRa", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 100, "[Frequency]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(165, 100, str(freq), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 100, " MHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 110, "[Bandwidth]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(165, 110, str(bw), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 110, " KHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 120, "[Output Power]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(186, 120, str(power), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 120, " dB", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        text_color = st7796_display.DARKGREEN if connection_flag == CONNECTED else st7796_display.RED if connection_flag == CONNECTING else st7796_display.BLUE
        st7796_display.draw_text(75, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(150, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', text_color, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(150, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 170, "<-------Send Info------->", st7796_display.ORANGE, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 180, "[Send Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(170, 180, str(send_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 200, "<------Receive Info------>", st7796_display.ORANGE, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 210, "[Receive Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(190, 210, str(receive_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_button(120, 250, 50, 90, st7796_display.ORANGE, "Reconnect", st7796_display.WHITE, text_size=1, rotation=1)
        st7796_display.draw_button(70, 330, 50, 90, st7796_display.PURPLE, "Try Again", st7796_display.WHITE, text_size=1, rotation=1)
        st7796_display.draw_button(170, 330, 50, 90, st7796_display.BLUE, "Next Test", st7796_display.WHITE, text_size=1, rotation=1)
                
    if connection_flag == CONNECTED:
        current_connection_flag = 1
        st7796_display.draw_text(75, 40, "SX1262 Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=1)
        st7796_display.draw_text(75, 80, "[Status]:Init successful", st7796_display.GREEN, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 90, "[Mode]:LoRa", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 100, "[Frequency]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(165, 100, str(freq), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 100, " MHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 110, "[Bandwidth]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(165, 110, str(bw), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 110, " KHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 120, "[Output Power]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(186, 120, str(power), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(200, 120, " dB", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 130, "[Local MAC]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(160, 130, str(local_mac), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        text_color = st7796_display.YELLOW if connection_flag == CONNECTED else st7796_display.RED if connection_flag == CONNECTING else st7796_display.BLACK
        st7796_display.draw_text(75, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(150, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', text_color, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 160, "[Connect MAC]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(180, 160, str(Connecting_mac), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 180, "<-------Send Info------->", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 190, "[Send Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(170, 190, str(send_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(75, 210, "<------Receive Info------>", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(75, 220, "[Receive Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(190, 220, str(receive_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        rssi_str = f"{sx.getRSSI():.1f}"
        st7796_display.draw_text(75, 230, "[Receive RSSI]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(190, 230, f"{rssi_str} dBm", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        snr_str = f"{sx.getSNR():.1f}"
        st7796_display.draw_text(75, 240, "[Receive SNR]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(190, 240, f"{snr_str} dBm", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_button(120, 250, 50, 90, st7796_display.ORANGE, "Reconnect", st7796_display.WHITE, text_size=1, rotation=1)
        st7796_display.draw_button(70, 330, 50, 90, st7796_display.PURPLE, "Try Again", st7796_display.WHITE, text_size=1, rotation=1)
        st7796_display.draw_button(170, 330, 50, 90, st7796_display.BLUE, "Next Test", st7796_display.WHITE, text_size=1, rotation=1)
    
    if current_connection_flag != previous_connection_flag:
        st7796_display.fillScreen(0, 0, st7796_display.WHITE)
        previous_connection_flag = current_connection_flag
        
            
    # Error counting logic
    if connection_flag == CONNECTING:
        error_count += 1
        print(f"[Error Count]: {error_count}")
        if error_count >= 3:  # Switch to UNCONNECTED after 5 failed attempts
            print("[Error Count]: Exceeded retries, resetting connection...")
            connection_flag = UNCONNECTED
            error_count = 0

    # Ensure the connection flag stays CONNECTED once it's set
    if connection_flag == CONNECTED:
        error_count = 0  # Reset error count once connected
        if time.ticks_ms() - last_receive_time > 10000: 
            print("[Connection Lost] No data received for 10 seconds, resetting connection...")
            connection_flag = UNCONNECTED

    time.sleep(0.5)  # Adjust the sleep as necessary


