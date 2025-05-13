from machine import Pin
import time

RELAY_1 = 8  
relay_pin = Pin(RELAY_1, Pin.OUT)

state = 0
relay_pin.value(state)

print("Ciallo")

while True:
    state = 1 - state
    relay_pin.value(state)
    
    time.sleep(3)