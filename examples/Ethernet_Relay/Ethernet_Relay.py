from machine import Pin, SPI
from wiznet5k import WIZNET5K
from wiznet5k_dhcp import DHCP
import time
import wiznet5k_socket  # Importing wiznet5k_socket

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
    time.sleep(1)
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
                print("Please insert the network cable and try again !");
                time.sleep(1)


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


def http_server():
    global HTML_Relay1_Flag
    static_ip_str = '.'.join(map(str, STATIC_IP))
    addr = wiznet5k_socket.getaddrinfo(static_ip_str, 80)[0][-1]  # Using wiznet5k_socket for address info
    s = wiznet5k_socket.socket()  # Create a socket using wiznet5k_socket
    s.bind(addr)
    s.listen(1)

    print("Server started at http://%s\n" % net.pretty_ip(net.ip_address))

    while True:
        try:
            cl, addr = s.accept()
            # print("New Client:", addr)
            cl.settimeout(0.5)
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


def main():
    print_hardware_status()
    print_link_status()
    network_init()
    http_server()


main()
