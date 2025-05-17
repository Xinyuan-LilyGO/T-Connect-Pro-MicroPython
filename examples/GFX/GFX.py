import st7796
import machine

print("Ciallo")

spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0, sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))
# Create an instance of ST7796
st7796_display = st7796.ST7796(spi=spi, cs=21, dc=41, rst=47, bl=46)

st7796_display.fillScreen(0, 0, st7796_display.WHITE)  # WHITE, BLACK, RED, GREEN, BLUE, YELLOW