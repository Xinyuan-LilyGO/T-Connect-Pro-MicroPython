from machine import Pin, SPI
from wiznet5k import WIZNET5K
from wiznet5k_dhcp import DHCP
import wiznet5k_socket as socket 
import time

# SPI initialization parameters
spi = SPI(1, baudrate=8_000_000, sck=Pin(12), mosi=Pin(11), miso=Pin(13, Pin.IN))
net = WIZNET5K(spi, cs=Pin(10, Pin.OUT), reset=Pin(48))

MAC = b"\xde\xad\xbe\xef\xfe\xed"
server = "220.181.38.150"   # www.baidu.com
port = 80

def print_hardware_status():
    time.sleep(2)
    chip = net.chip
    if chip == "":
        print("Ethernet No Hardware")
    elif chip == "W5100":
        print("Ethernet W5100 Discovery !")
    elif chip == "W5200":
        print("Ethernet W5200 Discovery !")
    elif chip == "W5500":
        print("Ethernet W5500 Discovery !")

def print_link_status():
    link_status = net.link_status
    if link_status == 0:
        print("Link status: Unknown")
    elif link_status == 1:
        print("Link status: ON")
    elif link_status == 2:
        print("Link status: OFF")
        print("The network cable is not connected !")
        while True:
            link_status = net.link_status
            if link_status == 1:
                print("Link status: ON")
                break
            elif link_status == 2:
                print("Please insert the network cable and try again !")
                time.sleep(1)

def network_init():
    global dhcp_client
    # Obtain the IP address using the DHCP client
    print("Trying to get an IP address using DHCP...")
    dhcp_client = DHCP(net, MAC)
    if dhcp_client.request_dhcp_lease():  # Request a DHCP
        print("My address: ", net.pretty_ip(net.ip_address))
    else:
        print("Failed to get an IP address using DHCP, trying manually")

def make_http_requests():
    while True:
        # Create a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            # Connect to the server
            try:
                start_time = time.ticks_ms()
                client.connect((server, port))
                # Send HTTP GET request
                request = "GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(server)
                client.send(request.encode())

                # Read the response
                content_length = None
                while True:
                    line = client.readline()
                    # print(line.decode())
                    if not line:
                        break
                    if line.startswith(b"Content-Length:"):
                        content_length = int(line.split(b": ")[1])
                print("Website Content-Length: {} bytes".format(content_length))
                print("")
                response = client.recv(1024)
                print(response.decode())
                end_time = time.ticks_ms()

                response_time = time.ticks_diff(end_time, start_time)
                print(f"Response time: {response_time} ms")
                
                # Measure throughput
                response_size = len(response)  # Size of the response in bytes
                throughput = (response_size / 1024.0) / (response_time / 1000.0)  # Kb/s
                print(f"Throughput: {throughput:.2f} Kb/s")
            except Exception as e:
                print("Connection failed: {}".format(e))
        time.sleep(5)  # Delay before next request

def main():
    print_hardware_status()
    print_link_status()
    network_init()
    print("")
    time.sleep(1)

    make_http_requests()  # Call the HTTP requests function

if __name__ == "__main__":
    main()