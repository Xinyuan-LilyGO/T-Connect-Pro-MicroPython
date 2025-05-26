# @Description: Touch test
# @Author: LILYGO
# @Date: 2025-05-19
# @LastEditTime: 2025-05-19
# @License: GPL 3.0

import CST226SE
import time

touch_sensor = CST226SE.CST226SE(39, 40, 47, 3)  # SDA, SCL, RST, INT pin numbers  
print("Ciallo")
while not touch_sensor.begin_touch_sensor():
    time.sleep(2)
print("CST226SE initialization successfully")

if __name__ == "__main__":
    start_time = time.ticks_ms()
    cycle_time = 0
        
    while True:
        current_time = time.ticks_ms()
        print(
            f"System running time: {time.ticks_diff(current_time, start_time) // 1000}s"
        )

        if touch_sensor.is_touch_detected():
            touch_interrupt_flag = False
            print(f"ID: {touch_sensor.device_id:#X}")
            touch_sensor.clear_touch_interrupt_flag()
            finger_number, touches, pressures = touch_sensor.read_touch_data()
            print(f"Fingers Number: {finger_number}")
            for i, (x, y) in enumerate(touches, start=1):
                print(f"Touch X{i}:{x} Y{i}:{y}")
            for i, pressure in enumerate(pressures, start=1):
                print(f"Touch{i} Pressure Value: {pressure}")
                
        time.sleep_ms(1000)
        if current_time > cycle_time:
            cycle_time += 5000

