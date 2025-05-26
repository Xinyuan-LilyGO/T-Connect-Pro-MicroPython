import st7796
import time
import machine
import CST226SE
import network
import sys
import urequests
from machine import Pin, SPI, CAN, UART
from wiznet5k import WIZNET5K
from wiznet5k_dhcp import DHCP
import wiznet5k_socket  # Importing wiznet5k_socket
from sx1262 import SX1262
import gc
import ustruct

# Initialize global variables
operation_done = False
transmit_flag = False
transmission_state = None
Connecting_mac = None
send_mac = None
send_data = 0
receive_data = 0
receive_can_data = 0
send_can_data = 0
error_count = 0
message_data = 0
# Define connection states
UNCONNECTED = 0
CONNECTING = 1
CONNECTED = 2
connection_flag = UNCONNECTED  # Initialize connection flag
current_connection_flag = 0
previous_connection_flag = 0

RS485_TX_1 = 4
RS485_RX_1 = 5
RS485_TX_2 = 17
RS485_RX_2 = 18
dev = CAN(0, tx=6, rx=7, mode=CAN.NORMAL, bitrate=1000000)
uart1 = UART(1, baudrate=115200, tx=Pin(RS485_TX_1), rx=Pin(RS485_RX_1))
uart2 = UART(2, baudrate=115200, tx=Pin(RS485_TX_2), rx=Pin(RS485_RX_2))
temp = 0
cycle_time = 0
isConnected1=False
isConnected2=False
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

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))
st7796_display = st7796.ST7796(spi=spi, cs=21, dc=41, rst=47, bl=46)

button_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
rotation = 0
finger_number = 0
Skip_Current_Test = False
state = 1
rotated_x, rotated_y = (0, 0)
rotated_x1, rotated_y1 = (0, 0)
rotated_x2, rotated_y2 = (0, 0)
rotated_x3, rotated_y3 = (0, 0)
rotated_x4, rotated_y4 = (0, 0)
rotated_x5, rotated_y5 = (0, 0)
previous_touches = [None] * 5
previous_pressures = [None] * 5
can_isConnect = 1
is_232Connect = 1
is_485Connect = 1
# Initialize SPI and W5500
spi = SPI(1, baudrate=8_000_000, sck=Pin(12), mosi=Pin(11), miso=Pin(13))
cs = Pin(10, Pin.OUT)
reset = Pin(48, Pin.OUT)
# Enter a MAC address and IP address for your controller below.
# The IP address will be dependent on your local network.
# gateway and subnet are optional:
# The MAC address must be an even number first !
MAC = b"\xde\xad\xbe\xef\xfe\xed"
STATIC_IP = (192, 168, 36, 114)
SUBNET = (255, 255, 0, 0)
GATEWAY = (192, 168, 36, 1)
DNS = (192, 168, 36, 1)
relay = Pin(8, Pin.OUT)  # Used for relay control
relay.value(1) 
HTML_Relay1_Flag = False
last_receive_time1 = time.ticks_ms()
last_receive_time2 = time.ticks_ms()

def GFX_Print_TEST(text):
    global Skip_Current_Test
    Skip_Current_Test = False
    while True:
        st7796_display.fillScreen(0, 0, st7796_display.WHITE)
        st7796_display.draw_text(int(SCREEN_WIDTH/2) -65, int(SCREEN_HEIGHT/4-15), "TEST", st7796_display.PALERED, st7796_display.WHITE, size=4, rotation=rotation)
        st7796_display.draw_text(int(SCREEN_WIDTH/4) -100, int(SCREEN_HEIGHT/4*1.5), text, st7796_display.BLACK, st7796_display.WHITE, size=2, rotation=rotation)
        st7796_display.draw_button(int(SCREEN_WIDTH/2) -78, int(SCREEN_HEIGHT/4*2.6), 40, 150, st7796_display.RED, "Skip Current Test", st7796_display.WHITE, text_size=1, rotation=rotation)
        if skip_button():
            Skip_Current_Test = True
            break
        st7796_display.draw_text(int(SCREEN_WIDTH/2) -20, int(SCREEN_HEIGHT/4*2.0), "3", st7796_display.RED, st7796_display.WHITE, size=4, rotation=rotation)
        if skip_button():
            Skip_Current_Test = True
            break
        time.sleep(1)
        if skip_button():
            Skip_Current_Test = True
            break
        st7796_display.draw_text(int(SCREEN_WIDTH/2) -20, int(SCREEN_HEIGHT/4*2.0), "2", st7796_display.RED, st7796_display.WHITE, size=4, rotation=rotation)
        if skip_button():
            Skip_Current_Test = True
            break
        time.sleep(1)
        if skip_button():
            Skip_Current_Test = True
            break
        st7796_display.draw_text(int(SCREEN_WIDTH/2) -20, int(SCREEN_HEIGHT/4*2.0), "1", st7796_display.RED, st7796_display.WHITE, size=4, rotation=rotation)
        if skip_button():
            Skip_Current_Test = True
            break
        time.sleep(1)
        break

def GFX_Print_1():
    st7796_display.draw_button(360, 80, 45, 100, st7796_display.ORANGE, "Try Again", st7796_display.WHITE, rotation=rotation)
    st7796_display.draw_button(360, 140, 45, 100, st7796_display.PURPLE, "Next Test", st7796_display.WHITE, rotation=rotation)

def touch_click():
    global rotated_x,rotated_y
    if touch_sensor.is_touch_detected():
        touch_interrupt_flag = False
        touch_sensor.clear_touch_interrupt_flag()
        # Read touch data
        finger_number, touches, pressures = touch_sensor.read_touch_data()
        if finger_number >= 1:
            x, y = touches[0]
            if rotation == 0:   # 0
                rotated_x, rotated_y = y, 222 - x
            elif rotation == 1: # 1
                rotated_x, rotated_y = x, y
            elif rotation == 2:  # 2
                rotated_x, rotated_y = 480 - y, x
            elif rotation == 3:    # 3
                rotated_x, rotated_y = 222 - x, 480 - y

def try_button():
    global rotated_x,rotated_y
    touch_click()
    if 360<rotated_x<430 and 30<rotated_y<80:
        rotated_x, rotated_y = (0, 0)
        return True
    else:
        return False
    
def next_button():
    global rotated_x,rotated_y
    touch_click()
    if 360<rotated_x<430 and 100<rotated_y<150:
        rotated_x, rotated_y = (0, 0)
        return True
    else:
        return False

def new_button():
    global rotated_x,rotated_y
    touch_click()
    if 360<rotated_x<430 and 155<rotated_y<220:
        rotated_x, rotated_y = (0, 0)
        return True
    else:
        return False
    
def skip_button():
    global rotated_x,rotated_y
    touch_click()
    if 150<rotated_x<280 and 140<rotated_y<230:
        rotated_x, rotated_y = (0, 0)
        return True
    else:
        return False
    
def Original_Test_1():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    st7796_display.draw_text(20, 80, "Touch Info", st7796_display.PALERED, st7796_display.WHITE, size=2, rotation=rotation)
    GFX_Print_1()
    st7796_display.draw_text(20, 110, "The Home button is triggered", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

def GFX_Print_Touch_Info_Loop():
    global rotated_x1,rotated_x2,rotated_x3,rotated_x4,rotated_x5,rotated_y1,rotated_y2,rotated_y3,rotated_y4,rotated_y5,finger_number,state
    st7796_display.draw_text(20, 100, f"ID: {touch_sensor.device_id:#X}", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    
    if touch_sensor.is_touch_detected():
        touch_interrupt_flag = False
        touch_sensor.clear_touch_interrupt_flag()
        # Read touch data
        finger_number, touches, pressures = touch_sensor.read_touch_data()
        
        if finger_number >= 1:
            x1, y1 = touches[0]
            if rotation == 0:   # 0
                rotated_x1, rotated_y1 = y1, 222 - x1
            elif rotation == 1: # 1
                rotated_x1, rotated_y1 = x1, y1
            elif rotation == 2:  # 2
                rotated_x1, rotated_y1 = 480 - y1, x1
            elif rotation == 3:    # 3
                rotated_x1, rotated_y1 = 222 - x1, 480 - y1
        if finger_number >= 2:
            x2, y2 = touches[1]
            if rotation == 0:   # 0
                rotated_x2, rotated_y2 = y2, 222 - x2
            elif rotation == 1: # 1
                rotated_x2, rotated_y2 = x2, y2
            elif rotation == 2:  # 2
                rotated_x2, rotated_y2 = 480 - y2, x2
            elif rotation == 3:    # 3
                rotated_x2, rotated_y2 = 222 - x2, 480 - y2
        if finger_number >= 3:
            x3, y3 = touches[2]
            if rotation == 0:   # 0
                rotated_x3, rotated_y3 = y3, 222 - x3
            elif rotation == 1: # 1
                rotated_x3, rotated_y3 = x3, y3
            elif rotation == 2:  # 2
                rotated_x3, rotated_y3 = 480 - y3, x3
            elif rotation == 3:    # 3
                rotated_x3, rotated_y3 = 222 - x3, 480 - y3
        if finger_number >= 4:
            x4, y4 = touches[3]
            if rotation == 0:   # 0
                rotated_x4, rotated_y4 = y4, 222 - x4
            elif rotation == 1: # 1
                rotated_x4, rotated_y4 = x4, y4
            elif rotation == 2:  # 2
                rotated_x4, rotated_y4 = 480 - y4, x4
            elif rotation == 3:    # 3
                rotated_x4, rotated_y4 = 222 - x4, 480 - y4
        if finger_number >= 5:
            x5, y5 = touches[4]
            if rotation == 0:   # 0
                rotated_x5, rotated_y5 = y5, 222 - x5
            elif rotation == 1: # 1
                rotated_x5, rotated_y5 = x5, y5
            elif rotation == 2:  # 2
                rotated_x5, rotated_y5 = 480 - y5, x5
            elif rotation == 3:    # 3
                rotated_x5, rotated_y5 = 222 - x5, 480 - y5
        if rotated_x1>480 or rotated_x1<0 or rotated_y1>240 or rotated_y1<0:
            st7796_display.draw_text(20, 110, "The Home button is triggered", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            state = 1
        else:
            state = 0
            st7796_display.draw_text(20, 110, f"Fingers Number: {finger_number}            ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(20, 120, f"Touch X{1}:{rotated_x1}   Y{1}:{rotated_y1}  ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(20, 130, f"Touch X{2}:{rotated_x2}   Y{2}:{rotated_y2}  ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(20, 140, f"Touch X{3}:{rotated_x3}   Y{3}:{rotated_y3}  ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(20, 150, f"Touch X{4}:{rotated_x4}   Y{4}:{rotated_y4}  ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(20, 160, f"Touch X{5}:{rotated_x5}   Y{5}:{rotated_y5}  ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    if state:
        st7796_display.draw_text(20, 110, "The Home button is triggered", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 120, "                        ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 130, "                        ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 140, "                        ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 150, "                        ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 160, "                        ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        rotated_x1, rotated_y1 = (0, 0)
        rotated_x2, rotated_y2 = (0, 0)
        rotated_x3, rotated_y3 = (0, 0)
        rotated_x4, rotated_y4 = (0, 0)
        rotated_x5, rotated_y5 = (0, 0)
    else:
        finger_number, touches, pressures = touch_sensor.read_touch_data()
        st7796_display.draw_text(20, 110, f"Fingers Number: {finger_number}            ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)


def Original_Test_2():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    st7796_display.draw_text(150, 140, "START", st7796_display.RED, st7796_display.WHITE, size=4, rotation=rotation)
    st7796_display.backlight = machine.PWM(st7796_display.backlight)
    for duty in range(1023, -1, -100): 
        st7796_display.backlight.freq(1000)
        st7796_display.backlight.duty(duty)
        time.sleep(0.1)  
    time.sleep(1)  
    for duty in range(0, 1024, 100): 
        st7796_display.backlight.freq(1000)
        st7796_display.backlight.duty(duty)
        time.sleep(0.1)  
    st7796_display.draw_text(150, 140, "FINISH", st7796_display.ORANGE, st7796_display.WHITE, size=4, rotation=rotation)
    GFX_Print_1()

def Original_Test_3():
    st7796_display.fillScreen(0, 0, st7796_display.RED)
    time.sleep(3)
    st7796_display.fillScreen(0, 0, st7796_display.GREEN)
    time.sleep(3)
    st7796_display.fillScreen(0, 0, st7796_display.BLUE)
    time.sleep(3)
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    time.sleep(3)
    st7796_display.fillScreen(0, 0, st7796_display.BLACK)
    st7796_display.draw_text(150, 140, "FINISH", st7796_display.ORANGE, st7796_display.BLACK, size=4, rotation=rotation)
    GFX_Print_1()

def Original_Test_4():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    # Initialize Wi-Fi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)

    print("\nScanning wifi")
    st7796_display.draw_text(0, 50, "Scanning wifi", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    wifi_list = wlan.scan()
    wifi_num = len(wifi_list)

    if wifi_num == 0:
        text = "\nWiFi scan complete!\nNo WiFi discovered\n"
        st7796_display.draw_text(0, 66, "WiFi scan complete", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(0, 74, "No WiFi discovered", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    else:
        text = "\nWiFi scan complete!\n"
        text += f"{wifi_num} WiFi networks discovered:\n\n"
        y_position = 90
        st7796_display.draw_text(0, 66, "WiFi scan complete", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(0, 74, f"{wifi_num} WiFi networks discovered", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        for i in range(wifi_num):
            ssid = wifi_list[i][0].decode('utf-8')  # SSID
            rssi = wifi_list[i][3]  # RSSI
            encryption = "*" if wifi_list[i][4] != 0 else ""
            text += f"{i + 1}: {ssid} ({rssi}) {encryption}\n"
            st7796_display.draw_text(0, y_position, f"{i + 1}: {ssid} ({rssi}) {encryption}", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            y_position += 8
            time.sleep(0.01)
    print(text)
    # Wait for a short moment before connecting to WiFi
    time.sleep(3)
    # Clear the console for the next phase
    print("\nConnecting to")
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    st7796_display.draw_text(0, 50, "Connecting to", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    WIFI_SSID = "xinyuandianzi"      # Replace with your SSID
    WIFI_PASSWORD = "AA15994823428"  # Replace with your password
    print(WIFI_SSID)
    st7796_display.draw_text(0, 58, WIFI_SSID, st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

    # Start connecting to the Wi-Fi
    wlan.connect(str(WIFI_SSID), str(WIFI_PASSWORD))

    # Set max waiting time for connection
    WIFI_CONNECT_WAIT_MAX = 10000
    last_tick = time.ticks_ms()

    Wifi_Connection_Flag = False
    x_pos = 0
    while not wlan.isconnected():
        sys.stdout.write(".")
        st7796_display.draw_text(x_pos, 66, ".", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        x_pos += 8
        time.sleep(0.1)
        if time.ticks_ms() - last_tick > WIFI_CONNECT_WAIT_MAX:
            break
        
    if wlan.isconnected():
        Wifi_Connection_Flag = True

    if Wifi_Connection_Flag:
        print("\nThe connection was successful!")
        st7796_display.draw_text(0, 72, "The connection was successful", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        print("Takes", time.ticks_ms() - last_tick, "ms")
        print("\nWiFi test passed!")
        st7796_display.draw_text(0, 88, "WiFi test passed", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    else:
        print("\nWiFi test error!")
        st7796_display.draw_text(0, 88, "WiFi test error", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    time.sleep(2)
    
def WIFI_HTTP_Download_File():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    
    fileDownloadUrl = "https://freetyst.nf.migu.cn/public/product9th/product45/2022/05/0716/2018%E5%B9%B409%E6%9C%8812%E6%97%A510%E7%82%B943%E5%88%86%E7%B4%A7%E6%80%A5%E5%86%85%E5%AE%B9%E5%87%86%E5%85%A5%E5%8D%8E%E7%BA%B3179%E9%A6%96/%E6%A0%87%E6%B8%85%E9%AB%98%E6%B8%85/MP3_128_16_Stero/6005751EPFG164228.mp3?channelid=02&msisdn=d43a7dcc-8498-461b-ba22-3205e9b6aa82&Tim=1728484238063&Key=0442fa065dacda7c"
    
    print("Initializing HTTP client...")

    # Start time for download tracking
    start_time = time.ticks_ms()
    useless_time = 0

    try:
        response = urequests.get(fileDownloadUrl, stream=True)  # Use stream mode for chunked response
        http_code = response.status_code

        if http_code == 200:  # HTTP_OK
            downloaded_size = 0
            last_report_time = time.ticks_ms()

            # Get file size (may be -1 if not available)
            file_size = int(response.headers.get('Content-Length', -1))

            if file_size == -1:
                print("File size is unknown. Proceeding with download...")
            else:
                print("Starting file download...")
                st7796_display.draw_text(0, 50, "Starting file download...", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
                print(f"File size: {file_size / 1024 / 1024:.2f} MB")
                st7796_display.draw_text(0, 58, f"File size: {file_size / 1024 / 1024:.2f} MB      ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

            # Start reading the response content
            while True:
                chunk = response.raw.read(4096)  # Read in 4KB chunks
                if not chunk:
                    break  # Break if there's no more data

                downloaded_size += len(chunk)
                current_time = time.ticks_ms()

                # Report every 3 seconds
                if time.ticks_diff(current_time, last_report_time) > 3000:
                    speed = (downloaded_size / 1024) / ((current_time - last_report_time) / 1000)  # KB/s
                    remaining_size = file_size - downloaded_size if file_size != -1 else -1
                    print(f"Download speed: {speed:.2f} KB/s")
                    st7796_display.draw_text(0, 74, f"Speed: {speed:.2f} KB/s       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
                    if remaining_size != -1:
                        print(f"Remaining file size: {remaining_size / 1024 / 1024:.2f} MB")
                        st7796_display.draw_text(0, 82, f"Size: {remaining_size / 1024 / 1024:.2f} MB       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
                    last_report_time = current_time

            response.close()  # Close HTTP connection

            end_time = time.ticks_ms()
            total_time = (end_time - start_time - useless_time) / 1000
            print("Download completed!")
            st7796_display.draw_text(0, 98, "Completed", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            print(f"Total download time: {total_time:.2f} s")
            st7796_display.draw_text(0, 106, f"Time: {total_time:.2f} s", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            average_speed = (downloaded_size / 1024) / total_time if total_time > 0 else 0
            print(f"Average download speed: {average_speed:.2f} KB/s")
            st7796_display.draw_text(0, 114, f"Speed: {average_speed:.2f} KB/s", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(150, 140, "FINISH", st7796_display.ORANGE, st7796_display.WHITE, size=4, rotation=rotation)
            GFX_Print_1()
        else:
            print("Failed to download")
            print(f"Error httpCode: {http_code}")

    except MemoryError:
        print("MemoryError: Not enough memory to complete the operation.")
    except Exception as e:
        print(f"An exception occurred: {str(e)}")
        gc.collect()  # Try to free up memory on error

def Original_Test_5():
    GFX_Print_RS485_Info()
    GFX_Print_1()
    st7796_display.draw_button(360, 200, 45, 100, st7796_display.PALERED, "Reconnect", st7796_display.WHITE, rotation=rotation)

# Send CAN message
def send_message():
    global counter,send_can_data
    msg_id = 0xF1
    msg_data = [1, 2, 3, 4, 5, 6, 7, 8]
    try:
        success = dev.send(msg_data, msg_id)
    except Exception as e:
        print(f"Error sending message: {e}")
        success = False
    if isConnect:
        print("Message queued for transmission")
        send_can_data += 1
    else:
        print("Failed to queue message for transmission, checking status...")

def rs_send_message():
    global temp
    temp += 1
    uart1.write(f"{temp}\n")
    time.sleep(0.01) 
    uart2.write(f"{temp}\n")
    time.sleep(0.01) 
    
# Receive CAN message
def receive_message():
    global isConnect, last_receive_time, dev, receive_can_data
    if dev.any():
        # If we receive a message, reset the connection timer
        last_receive_time = time.time()  # Update the last receive time
        isConnect = True

        data = dev.recv()
        message_id = data[0]
        is_extended = data[1]
        is_rtr = data[2]
        message_data = data[3]

        if is_extended:
            print("Message is in Extended Format")
        else:
            print("Message is in Standard Format")

        print(f"ID: 0x{message_id:X}")
        if not is_rtr:
            for i in range(len(message_data)):
                print(f"Data [{i}] = {message_data[i]}")
            receive_can_data += 1
            print("")

    # If 3 seconds have passed without receiving a message, set isConnect to False
    elif time.time() - last_receive_time > 3:
        isConnect = False

def rs_receive_message():
    global isConnected1, isConnected2, last_receive_time1, last_receive_time2
    current_time = time.ticks_ms()
    if uart1.any():
        data = uart1.read()
        if data:
            decoded_data = safe_decode(data)
            if decoded_data:
                print("RS485_1 receive data:", decoded_data.strip())
                last_receive_time1 = current_time  
                isConnected1 = True
    else:
        if time.ticks_diff(current_time, last_receive_time1) > 3000:
            isConnected1 = False 
    
    if uart2.any():
        data = uart2.read()
        if data:
            decoded_data = safe_decode(data)
            if decoded_data:
                print("RS485_2 receive data:", decoded_data.strip())
                last_receive_time2 = current_time  
                isConnected2 = True
    else:
        if time.ticks_diff(current_time, last_receive_time2) > 3000:
            isConnected2 = False 
    
    print(isConnected1)
    print(isConnected2)
    
def safe_decode(data):
    try:
        return data.decode('utf-8')
    except UnicodeError:
        return None
    
def GFX_Print_RS485CAN_Info_Loop():
    GFX_Print_485_CAN_Info_Loop()


def GFX_Print_485_CAN_Info_Loop():
    global isConnect, receive_can_data, send_can_data, can_isConnect
    global isConnected1, isConnected2, is_232Connect, is_485Connect
    global connection_start_time_232, connection_start_time_485, connection_start_time_can

    can_current_time = time.time()

    # 232 Connection Check
    if isConnected1 is True:
        st7796_display.draw_text(55, 131, f"[Connect]: Connected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(55, 139, f"[Receive Data]: {receive_can_data}         ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        can_isConnect = 1
        connection_start_time_232 = None  # Reset the timer when connected
    elif isConnected1 is not True:
        if is_232Connect == 0:
            if connection_start_time_232 is None:
                connection_start_time_232 = can_current_time  # Start the timer
            if (can_current_time - connection_start_time_232) >= 3:
                is_232Connect = 1  # Set to 1 if more than 3 seconds
            st7796_display.draw_text(55, 131, f"[Connect]: Connecting       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 139, f"[Send Data]: {send_can_data}          ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        else:
            st7796_display.draw_text(55, 131, f"[Connect]: Unconnected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 139, f"                                 ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

    # 485 Connection Check
    if isConnected2 is True:
        st7796_display.draw_text(55, 168, f"[Connect]: Connected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(55, 176, f"[Receive Data]: {receive_can_data}         ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        can_isConnect = 1
        connection_start_time_485 = None  # Reset the timer when connected
    elif isConnected2 is not True:
        if is_485Connect == 0:
            if connection_start_time_485 is None:
                connection_start_time_485 = can_current_time  # Start the timer
            if (can_current_time - connection_start_time_485) >= 3:
                is_485Connect = 1  # Set to 1 if more than 3 seconds
            st7796_display.draw_text(55, 168, f"[Connect]: Connecting       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 176, f"[Send Data]: {send_can_data}          ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        else:
            st7796_display.draw_text(55, 168, f"[Connect]: Unconnected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 176, f"                                 ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

    # CAN Connection Check
    if isConnect is True:
        st7796_display.draw_text(55, 216, f"[Connect]: Connected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(55, 224, f"[Receive Data]: {receive_can_data}         ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        can_isConnect = 1
        connection_start_time_can = None  # Reset the timer when connected
    elif isConnect is not True:
        if can_isConnect == 0:
            if connection_start_time_can is None:
                connection_start_time_can = can_current_time  # Start the timer
            if (can_current_time - connection_start_time_can) >= 3:
                can_isConnect = 1  # Set to 1 if more than 3 seconds
            st7796_display.draw_text(55, 216, f"[Connect]: Connecting       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 224, f"[Send Data]: {send_can_data}          ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
        else:
            st7796_display.draw_text(55, 216, f"[Connect]: Unconnected       ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
            st7796_display.draw_text(55, 224, f"                                 ", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    
def GFX_Print_RS485_Info():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    st7796_display.draw_text(30, 65, "RS485232CAN Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=rotation)
    st7796_display.draw_text(40, 90, "[RS485232]:115200 bps/s", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    st7796_display.draw_text(40, 98, "[CAN]:1 mbit/s", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    
    st7796_display.draw_text(40, 115, "<----------UART Info---------->", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    st7796_display.draw_text(40, 123, "[RS232]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    st7796_display.draw_text(40, 160, "[RS485]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    
    st7796_display.draw_text(40, 200, "<----------CAN Info---------->", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)
    st7796_display.draw_text(40, 208, "[CAN]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=rotation)

def GFX_Print_RS485_Info_Loop():
    pass

def Original_Test_6():
    GFX_Print_Ethernet_Info()
    GFX_Print_1()
    st7796_display.draw_button(360, 200, 45, 100, st7796_display.PALERED, "Relay Test", st7796_display.WHITE, rotation=rotation)
    GFX_Print_Ethernet_Info_Loop()
    
def ethernet_reset():
    reset.value(1)
    time.sleep_ms(250)
    reset.value(0)
    time.sleep_ms(50)
    reset.value(1)
    time.sleep_ms(350)

def print_hardware_status():
    global net
    ethernet_reset()
    time.sleep(0.5)
    net = WIZNET5K(spi, cs=cs, reset=None, mac=MAC)
    chip = net.chip
    if chip == "":
        print("Ethernet No Hardware")
    elif chip == "W5100":
        print("Ethernet W5100 Discovery !")
    elif chip == "W5200":
        print("Ethernet W5200 Discovery !")
    elif chip == "w5500":
        print("Ethernet W5500 Discovery !")

def cable_link_status():
    global HTML_Relay1_Flag,eth_relay_info
    link_status = net.link_status
    if link_status == 0:
        print("Link status: Unknown")
    elif link_status == 1:
        print("Link status: ON")
        st7796_display.draw_text(20, 88, "[State]:", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(36, 96, "Initialization successful", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        network_init() # network init
        static_ip_str = '.'.join(map(str, STATIC_IP))
        addr = wiznet5k_socket.getaddrinfo(static_ip_str, 80)[0][-1]  # Using wiznet5k_socket for address info
        s = wiznet5k_socket.socket()  # Create a socket using wiznet5k_socket
        s.bind(addr)
        s.listen(1)
        s.settimeout(0.5)
        print("Server started at http://%s\n" % net.pretty_ip(net.ip_address))
        while True:
            try:
                if new_button():
                    HTML_Relay1_Flag = not HTML_Relay1_Flag
                    relay.value(0 if HTML_Relay1_Flag else 1)
                if try_button():
                    GFX_Print_TEST("Ethernet Relay Test")
                    Original_Test_6()
                    break
                if next_button():
                    eth_relay_info = False
                    break
                link_status = net.link_status
                if link_status is not 1:
                    break
                cl_addr = s.accept()
                if cl_addr is None:
                    continue  # No client connected, try again
                cl, addr = cl_addr
                # print("New Client:", addr)
                cl.settimeout(0.05)
                request = cl.recv(1024).decode()
                # print("Request received:\n", request)
                if "GET /RELAY_1" in request:
                    HTML_Relay1_Flag = not HTML_Relay1_Flag
                    relay.value(0 if HTML_Relay1_Flag else 1)
                    # print("Relay 1 state changed to:", "ON" if HTML_Relay1_Flag else "OFF")
                    
                response = """\
    HTTP/1.1 200 OK
    Content-Type: text/html

    <head><meta charset="UTF-8"></head><body><div align="center"><h2>Relay Ethernet Server Test</h2><br />
    <h3>Click <a href="/RELAY_1">here</a> to change the Relay 1 state.<br></h3>
    """
                cl.send(response.encode())
                cl.close()
                # print("Client Disconnected.")
                
            except Exception as e:
                print("Socket error:", e)
                time.sleep(1)

        
    elif link_status == 2:
        if new_button():
            HTML_Relay1_Flag = not HTML_Relay1_Flag
            relay.value(0 if HTML_Relay1_Flag else 1)
        if try_button():
            GFX_Print_TEST("Ethernet Relay Test")
            Original_Test_6()
        if next_button():
            eth_relay_info = False
        print("Link status: OFF")
        print("The network cable is not connected !")
        print("Please insert the network cable and try again !");
        st7796_display.draw_text(20, 88, "[State]:", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(36, 96, "Initialization failed    ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 104, "[Assertion]:                 ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 114, "  Please insert the network cable   ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 124, "                                  ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 134, "                                  ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)

def network_init():
    global dhcp_client
    # Obtain the IP address using the DHCP client
    print("Trying to get an IP address using DHCP...")
    dhcp_client = DHCP(net, MAC)
    if dhcp_client.request_dhcp_lease():  # Request a DHCP
        print("-------------------------")
        print("[INFO] Configuring random DHCP successfully !")
        print("")
        print("[DHCP] IP Address: ", net.pretty_ip(net.ip_address))
        ip_address, subnet_mask, gateway, dns = net.ifconfig
        print("[DHCP] Subnet Mask: ", net.pretty_ip(subnet_mask))
        print("[DHCP] Gateway: ", net.pretty_ip(gateway))
        print("[DHCP] DNS: ", net.pretty_ip(dns))
        print("-------------------------\n")

        st7796_display.draw_text(20, 104, f"[IP address]: {net.pretty_ip(net.ip_address)}", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 114, f"[Subnet mask]: {net.pretty_ip(subnet_mask)}       ", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 124, f"[Gateway]: {net.pretty_ip(gateway)}", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
        st7796_display.draw_text(20, 134, f"[DNS]: {net.pretty_ip(dns)}", st7796_display.PURPLE, st7796_display.WHITE, size=1, rotation=rotation)
    else:
        print("-------------------------")
        print("[INFO] Configuring random DHCP failed !")
        print("[INFO] Configuring static IP...")
        print("[Static] IP Address: ", net.pretty_ip(net.ip_address))
        ip_address, subnet_mask, gateway, dns = net.ifconfig
        print("[Static] Subnet Mask: ", net.pretty_ip(subnet_mask))
        print("[Static] Gateway: ", net.pretty_ip(gateway))
        print("[Static] DNS: ", net.pretty_ip(dns))
        print("-------------------------\n")
 
def GFX_Print_Ethernet_Info():
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    st7796_display.draw_text(30, 65, "Eth Relay Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=rotation)

def GFX_Print_Ethernet_Info_Loop():
    print_hardware_status()

def Original_Test_8():
    global initiating_node,transmission_state,transmit_flag,state,previous_connection_flag,last_receive_time,local_mac,sx,freq,bw,power
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
    st7796_display.fillScreen(0, 0, st7796_display.WHITE)
    
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
#     previous_connection_flag = None
    last_receive_time = time.ticks_ms()
    
def Original_Test_8_Loop():
    global operation_done, transmit_flag, connection_flag, receive_data, last_receive_time, Connecting_mac, send_data, current_connection_flag, previous_connection_flag,error_count

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
        st7796_display.draw_text(0, 50, "SX1262 Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=0)
        st7796_display.draw_text(15, 80, "[Status]:Init successful", st7796_display.GREEN, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(15, 90, "[Mode]:LoRa", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(14, 100, "[Frequency]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(105, 100, str(freq), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(140, 100, " MHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(15, 110, "[Bandwidth]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(105, 110, str(bw), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(140, 110, " KHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(15, 120, "[Output Power]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(126, 120, str(power), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(140, 120, " dB", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        text_color = st7796_display.DARKGREEN if connection_flag == CONNECTED else st7796_display.RED if connection_flag == CONNECTING else st7796_display.BLUE
        st7796_display.draw_text(15, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(90, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', text_color, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(15, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(90, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(15, 170, "<-------Send Info------->", st7796_display.ORANGE, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(15, 180, "[Send Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(110, 180, str(send_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)

        st7796_display.draw_text(15, 200, "<------Receive Info------>", st7796_display.ORANGE, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(15, 210, "[Receive Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
        st7796_display.draw_text(130, 210, str(receive_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=0)
                
    if connection_flag == CONNECTED:
        current_connection_flag = 1
        st7796_display.draw_text(15, 40, "SX1262 Info", st7796_display.PURPLE, st7796_display.WHITE, size=2, rotation=1)
        st7796_display.draw_text(15, 80, "[Status]:Init successful", st7796_display.GREEN, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(15, 90, "[Mode]:LoRa", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 100, "[Frequency]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(105, 100, str(freq), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(140, 100, " MHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 110, "[Bandwidth]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(105, 110, str(bw), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(140, 110, " KHz", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 120, "[Output Power]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(126, 120, str(power), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(140, 120, " dB", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 130, "[Local MAC]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(100, 130, str(local_mac), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        text_color = st7796_display.YELLOW if connection_flag == CONNECTED else st7796_display.RED if connection_flag == CONNECTING else st7796_display.BLACK
        st7796_display.draw_text(15, 150, "[Connect]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(90, 150, 'CONNECTED    ' if connection_flag == CONNECTED else 'CONNECTING  ' if connection_flag == CONNECTING else 'UNCONNECTED', text_color, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 160, "[Connect MAC]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(120, 160, str(Connecting_mac), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 180, "<-------Send Info------->", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(15, 190, "[Send Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(110, 190, str(send_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        st7796_display.draw_text(15, 210, "<------Receive Info------>", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(15, 220, "[Receive Data]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(130, 220, str(receive_data), st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        rssi_str = f"{sx.getRSSI():.1f}"
        st7796_display.draw_text(15, 230, "[Receive RSSI]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(130, 230, f"{rssi_str} dBm", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        
        snr_str = f"{sx.getSNR():.1f}"
        st7796_display.draw_text(15, 240, "[Receive SNR]:", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
        st7796_display.draw_text(130, 240, f"{snr_str} dBm", st7796_display.BLACK, st7796_display.WHITE, size=1, rotation=1)
    
    # Error counting logic
    if connection_flag == CONNECTING:
        error_count += 1
        print(f"[Error Count]: {error_count}")
        if error_count >= 3:  # Switch to UNCONNECTED after 5 failed attempts
            print("[Error Count]: Exceeded retries, resetting connection...")
            connection_flag = UNCONNECTED
            error_count = 0
            
    if current_connection_flag != previous_connection_flag:
        st7796_display.fillScreen(0, 0, st7796_display.WHITE)
        GFX_Print_1()
        st7796_display.draw_button(360, 200, 45, 100, st7796_display.PALERED, "Reconnect", st7796_display.WHITE, rotation=rotation)
        previous_connection_flag = current_connection_flag
        

    # Ensure the connection flag stays CONNECTED once it's set
    if connection_flag == CONNECTED:
        error_count = 0  # Reset error count once connected
        if time.ticks_ms() - last_receive_time > 10000: 
            print("[Connection Lost] No data received for 10 seconds, resetting connection...")
            connection_flag = UNCONNECTED

    time.sleep(0.5)  # Adjust the sleep as necessary
    
def Original_Test_Loop():
    global rotated_x1,rotated_x2,rotated_x3,rotated_x4,rotated_x5,rotated_y1,rotated_y2,rotated_y3,rotated_y4,rotated_y5,Skip_Current_Test, HTML_Relay1_Flag,eth_relay_info,connection_flag, dev, polling_rate, counter, cycle_time, isConnect, last_receive_time,can_isConnect,is_232Connect,is_485Connect,uart1,uart2,RS485_1_Count,RS485_2_Count
    
    gc.collect()
    GFX_Print_TEST("Touch Test")
    # touch test
    if Skip_Current_Test is not True:
        Original_Test_1()
        while True:
            GFX_Print_Touch_Info_Loop()
            if try_button():
                rotated_x1, rotated_y1 = (0, 0)
                rotated_x2, rotated_y2 = (0, 0)
                rotated_x3, rotated_y3 = (0, 0)
                rotated_x4, rotated_y4 = (0, 0)
                rotated_x5, rotated_y5 = (0, 0)
                GFX_Print_TEST("Touch Test")
                Original_Test_1()
            if next_button():
                rotated_x1, rotated_y1 = (0, 0)
                rotated_x2, rotated_y2 = (0, 0)
                rotated_x3, rotated_y3 = (0, 0)
                rotated_x4, rotated_y4 = (0, 0)
                rotated_x5, rotated_y5 = (0, 0)
                break
    gc.collect()                
                    
    # LCD Backlight Test
    GFX_Print_TEST("LCD Backlight Test")
    if Skip_Current_Test is not True:
        Original_Test_2()
        while True:
            if try_button():
                GFX_Print_TEST("LCD Backlight Test")
                Original_Test_2()
            if next_button():
                break
    
    gc.collect()
    GFX_Print_TEST("LCD Color Test")
    if Skip_Current_Test is not True:
        Original_Test_3()
        while True:
            if try_button():
                GFX_Print_TEST("LCD Color Test")
                Original_Test_3()
            if next_button():
                break
    
    gc.collect()        
    GFX_Print_TEST("WIFI STA Test")
    if Skip_Current_Test is not True:
        Original_Test_4()
        WIFI_HTTP_Download_File()
        while True:
            if try_button():
                GFX_Print_TEST("WIFI STA Test")
                Original_Test_4()
                WIFI_HTTP_Download_File()
            if next_button():
                break
            
    gc.collect()
    GFX_Print_TEST("RS485232CAN Test") 
    if Skip_Current_Test is not True:
        # Define CAN device initialization
        Original_Test_5()
        # Interval for polling rate (1 second)
        polling_rate = 1  # 1 second
        # Counter for the CAN message
        counter = 0
        cycle_time = 0
        # Flag to track connection status
        isConnect = False
        last_receive_time = time.time()  # Record the last time a message was received
        while True:
            current_time = time.time()
            if current_time > cycle_time:
                send_message()
                rs_send_message()
                cycle_time = current_time + polling_rate  # Set next cycle time to 1 second
            # Receive messages
            receive_message()
            rs_receive_message()
            # Sleep for a short time to simulate polling delay (10ms)
            time.sleep(0.01)
            GFX_Print_RS485CAN_Info_Loop()
            if try_button():
                GFX_Print_TEST("RS485232CAN Test")
                Original_Test_5()
            if next_button():
                break
            if new_button():
                can_isConnect = 0
                is_232Connect = 0
                is_485Connect = 0
    
    gc.collect()
    GFX_Print_TEST("Ethernet Relay Test")
    eth_relay_info = True
    if Skip_Current_Test is not True:
        Original_Test_6()
        while eth_relay_info:
            cable_link_status()
            
    gc.collect()
    GFX_Print_TEST("SX1262 callback distance test")
    if Skip_Current_Test is not True:
        Original_Test_8()
        st7796_display.fillScreen(0, 0, st7796_display.WHITE)
        GFX_Print_1()
        st7796_display.draw_button(360, 200, 45, 100, st7796_display.PALERED, "Reconnect", st7796_display.WHITE, rotation=rotation)
        while True:
            Original_Test_8_Loop()
            if try_button():
                GFX_Print_TEST("SX1262 callback distance test")
                Original_Test_8()
            if next_button():
                break
            if new_button():
                connection_flag = CONNECTING
    gc.collect()       
            
    
def setup():
    global touch_sensor
    touch_sensor = CST226SE.CST226SE(39, 40, 47, 3)  # SDA, SCL, RST, INT pin numbers  
    while not touch_sensor.begin_touch_sensor():  # CST226SE initialization ?
         time.sleep(2)
    while uart1.any():
        uart1.read()
    while uart2.any():
        uart2.read()

if __name__ == "__main__":
    setup()   
    while True:
        Original_Test_Loop()
