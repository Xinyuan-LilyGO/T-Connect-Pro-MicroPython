from sx1262 import SX1262
import time

# Initialize global variables
operation_done = False
transmit_flag = False
transmission_state = None

# Define the callback function
def cb(events):
    global operation_done, transmit_flag, transmission_state
    if events & SX1262.RX_DONE:  # Check if the RX_DONE event has occurred
        msg, err = sx.recv()  # Receive the message
        error = SX1262.STATUS.get(err, "Unknown error")
        
        # Print received message
        print("[SX1262] Received packet!")
        print("[SX1262] Data:\t\t{}".format(msg.decode('utf-8')))
        print("[SX1262] RSSI:\t\t{} dBm".format(sx.getRSSI()))
        print("[SX1262] SNR:\t\t{} dB".format(sx.getSNR()))
        
        operation_done = True  # Set the operation done flag
        transmit_flag = False   # Reset transmit flag

    elif events & SX1262.TX_DONE:  # Check if the TX_DONE event has occurred
        print("transmission finished!")
        operation_done = True  # Set the operation done flag
        transmit_flag = True    # Set transmit flag

# Initialize SX1262 instance with ESP32S3 pin configuration
sx = SX1262(spi_bus=1, clk=12, mosi=11, miso=13, cs=14, irq=45, rst=42, gpio=38)

# LoRa mode configuration
sx.begin(freq=923, bw=500.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# Set the callback function
sx.setBlockingCallback(False, cb)

# Uncomment the line below for the initiating node
initiating_node = True  # Set to True for the initiating node, False for the responding node

def setup():
    print("[SX1262] Initializing ... ")
    
    if initiating_node:
        # Send the first packet on this node
        print("[SX1262] Sending first packet ... ")
        transmission_state = sx.send(b'Hello World!')
        
        # Check if transmission_state is a tuple (12, 0)
        if isinstance(transmission_state, tuple):
            if transmission_state[0] == 0:
                print("transmission finished!")
            else:
                print(f"failed, code {transmission_state[0]}")
        else:
            print("Unexpected TX state format")
        
        transmit_flag = True
    else:
        # Start listening for LoRa packets on this node
        print("[SX1262] Starting to listen ... ")
        state = sx.startReceive()
        print("RX state: {}".format(SX1262.STATUS.get(state, "Unknown error")))

# Call the setup function to initialize the radio
setup()

while True:
    # Check if the previous operation finished
    if operation_done:
        # Reset flag
        operation_done = False

        if transmit_flag:
            # The previous operation was transmission, listen for response
            sx.startReceive()
            transmit_flag = False
        else:
            # If we received a packet, send another one
            print("[SX1262] Sending another packet ... ")
            transmission_state = sx.send(b'Hello World!')
            transmit_flag = True
            
    time.sleep(1)  # Adjust the delay as needed