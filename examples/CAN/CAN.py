import time
import CAN

# Define CAN device initialization
dev = CAN(0, extframe=False, tx=6, rx=7, mode=CAN.NORMAL, bitrate=1000000)

# Interval for polling rate (1 second)
polling_rate = 1  # 1 second

# Counter for the CAN message
counter = 0
cycle_time = 0

# Flag to track connection status
isConnect = False
last_receive_time = time.time()  # Record the last time a message was received

# Send CAN message
def send_message():
    global counter
    msg_id = 0xF1
    msg_data = [1, 2, 3, 4, 5, 6, 7, 8]

    success = dev.send(msg_data, msg_id)

    if isConnect:
        print("Message queued for transmission")
    else:
        print("Failed to queue message for transmission, checking status...")

# Receive CAN message
def receive_message():
    global isConnect, last_receive_time

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
            print("")

    # If 3 seconds have passed without receiving a message, set isConnect to False
    elif time.time() - last_receive_time > 3:
        isConnect = False

# Main loop for CAN communication
def main():
    global cycle_time

    while True:
        # Check if a second has passed
        current_time = time.time()
        if current_time > cycle_time:
            send_message()
            cycle_time = current_time + polling_rate  # Set next cycle time to 1 second

        # Receive messages
        receive_message()

        # Sleep for a short time to simulate polling delay (10ms)
        time.sleep(0.01)

if __name__ == "__main__":
    main()
