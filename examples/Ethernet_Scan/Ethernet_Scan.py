from machine import Pin, SPI
from wiznet5k import WIZNET5K
import time

# SPI initialization parameters
spi = SPI(1, baudrate=8_000_000, sck=Pin(12), mosi=Pin(11), miso=Pin(13, Pin.IN))
net = WIZNET5K(spi, cs=Pin(10, Pin.OUT), reset=Pin(48))

def print_hardware_status():
    chip = net.chip
    if chip == "":
        print("Ethernet No Hardware")
    elif chip == "W5100":
        print("Ethernet W5100")
    elif chip == "W5200":
        print("Ethernet W5200")
    elif chip == "w5500":
        print("Ethernet W5500")

def print_link_status():
    link_status = net.link_status
    if link_status == 0:
        print("Link status: Unknown")
    elif link_status == 1:
        print("Link status: ON")
    elif link_status == 2:
        print("Link status: OFF")

def main():
    while True:
        print_hardware_status()
        print_link_status()  # Print the connection status
        print("")
        time.sleep(1)

if __name__ == "__main__":
    main()
