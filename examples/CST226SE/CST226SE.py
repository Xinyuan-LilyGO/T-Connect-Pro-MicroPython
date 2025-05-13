# @Description: Touch test
# @Author: LILYGO
# @Date: 2025-05-07
# @LastEditTime: 2025-05-07
# @License: GPL 3.0

from machine import Pin, I2C
import time

CST226SE_RD_DEVICE_X1POSH = 0x01  # X1posH
CST226SE_RD_DEVICE_X1POSL = 0x03  # X1posL
CST226SE_RD_DEVICE_Y1POSH = 0x02  # Y1posH
CST226SE_RD_DEVICE_Y1POSL = 0x03  # Y1posL
CST226SE_RD_DEVICE_X2POSH = 0x08  # X2posH
CST226SE_RD_DEVICE_X2POSL = 0x0A  # X2posL
CST226SE_RD_DEVICE_Y2POSH = 0x09  # Y2posH
CST226SE_RD_DEVICE_Y2POSL = 0x0A  # Y2posL
CST226SE_RD_DEVICE_X3POSH = 0x0D  # X3posH
CST226SE_RD_DEVICE_X3POSL = 0x0F  # X3posL
CST226SE_RD_DEVICE_Y3POSH = 0x0E  # Y3posH
CST226SE_RD_DEVICE_Y3POSL = 0x0F  # Y3posL
CST226SE_RD_DEVICE_X4POSH = 0x12  # X4posH
CST226SE_RD_DEVICE_X4POSL = 0x14  # X4posL
CST226SE_RD_DEVICE_Y4POSH = 0x13  # Y4posH
CST226SE_RD_DEVICE_Y4POSL = 0x14  # Y4posL
CST226SE_RD_DEVICE_X5POSH = 0x17  # X5posH
CST226SE_RD_DEVICE_X5POSL = 0x19  # X5posL
CST226SE_RD_DEVICE_Y5POSH = 0x18  # Y5posH
CST226SE_RD_DEVICE_Y5POSL = 0x19  # Y5posL
CST226SE_RD_DEVICE_TOUCH1_PRESSURE_VALUE = 0x04  # Touch the pressure value of 1 finger
CST226SE_RD_DEVICE_TOUCH2_PRESSURE_VALUE = 0x07  # Touch the pressure value of 2 finger
CST226SE_RD_DEVICE_TOUCH3_PRESSURE_VALUE = 0x0C  # Touch the pressure value of 3 finger
CST226SE_RD_DEVICE_TOUCH4_PRESSURE_VALUE = 0x11  # Touch the pressure value of 4 finger
CST226SE_RD_DEVICE_TOUCH5_PRESSURE_VALUE = 0x16  # Touch the pressure value of 5 finger

# Define the pins and addresses
IIC_SDA_PIN = 39  # Replace with your actual SDA pin number
IIC_SCL_PIN = 40  # Replace with your actual SCL pin number
TOUCH_RST_PIN = 47  # Replace with your actual RST pin number
TOUCH_INT_PIN = 3  # Replace with your actual INT pin number
CST226SE_DEVICE_ADDRESS = 0x5A  # Replace with the actual device address if different

# Initialize I2C bus
i2c = I2C(1, scl=Pin(IIC_SCL_PIN), sda=Pin(IIC_SDA_PIN), freq=400000)

# Initialize touch interrupt flag
touch_interrupt_flag = False


def touch_interrupt_handler(pin):
    global touch_interrupt_flag
    touch_interrupt_flag = True


# Set up interrupt pin
touch_int_pin = Pin(TOUCH_INT_PIN, Pin.IN)
touch_int_pin.irq(trigger=Pin.IRQ_FALLING, handler=touch_interrupt_handler)

# Reset the touch sensor
touch_rst_pin = Pin(TOUCH_RST_PIN, Pin.OUT)
touch_rst_pin.off()
time.sleep_ms(100)
touch_rst_pin.on()


def read_register(i2c, addr, reg):
    return i2c.readfrom_mem(addr, reg, 1)[0]


def write_register(i2c, addr, reg, val):
    i2c.writeto_mem(addr, reg, bytes([val]))


def begin_touch_sensor():
    time.sleep(1)
    try:
        device_id = read_register(i2c, CST226SE_DEVICE_ADDRESS, 0x06)
        print(f"ID: {device_id:#X}")
        return True
    except OSError as e:
        print(f"CST226SE initialization fail: {e}")
        return False


def map_value(value, in_min, in_max, out_min, out_max):
    """Linear mapping function"""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def read_touch_data():
    finger_number = read_register(i2c, CST226SE_DEVICE_ADDRESS, 0x05)
    touches = []
    pressures = []

    for i in range(1, finger_number + 1):
        try:
            # Obtain the register address
            x_high_addr = globals()[f"CST226SE_RD_DEVICE_X{i}POSH"]
            x_low_addr = globals()[f"CST226SE_RD_DEVICE_X{i}POSL"]
            y_high_addr = globals()[f"CST226SE_RD_DEVICE_Y{i}POSH"]
            y_low_addr = globals()[f"CST226SE_RD_DEVICE_Y{i}POSL"]
        except KeyError as e:
            continue

        # Read the original data
        x_high = read_register(i2c, CST226SE_DEVICE_ADDRESS, x_high_addr)
        x_low = read_register(i2c, CST226SE_DEVICE_ADDRESS, x_low_addr)
        y_high = read_register(i2c, CST226SE_DEVICE_ADDRESS, y_high_addr)
        y_low = read_register(i2c, CST226SE_DEVICE_ADDRESS, y_low_addr)

        # Analyze the X and Y coordinates (12 bits)
        x = ((x_high & 0xFF) << 4) | ((x_low & 0xF0) >> 4)
        y = ((y_high & 0xFF) << 4) | (y_low & 0x0F)

        # Read the pressure value
        try:
            pressure_addr = globals()[f"CST226SE_RD_DEVICE_TOUCH{i}_PRESSURE_VALUE"]
            pressure = read_register(i2c, CST226SE_DEVICE_ADDRESS, pressure_addr)
        except KeyError as e:
            continue

        touches.append((x, y))
        pressures.append(pressure)

    return finger_number, touches, pressures


if __name__ == "__main__":
    print("Ciallo")
    while not begin_touch_sensor():
        time.sleep(2)
    print("CST226SE initialization successfully")

    start_time = time.ticks_ms()
    cycle_time = 0
    while True:
        current_time = time.ticks_ms()
        print(
            f"System running time: {time.ticks_diff(current_time, start_time) // 1000}s"
        )

        if touch_interrupt_flag:
            touch_interrupt_flag = False
            device_id = read_register(i2c, CST226SE_DEVICE_ADDRESS, 0x06)
            print(f"ID: {device_id:#X}")
            finger_number, touches, pressures = read_touch_data()
            print(f"Fingers Number: {finger_number}")
            for i, (x, y) in enumerate(touches, start=1):
                print(f"Touch X{i}:{x} Y{i}:{y}")
            for i, pressure in enumerate(pressures, start=1):
                print(f"Touch{i} Pressure Value: {pressure}")
        time.sleep_ms(1000)
        if current_time > cycle_time:
            cycle_time += 5000
