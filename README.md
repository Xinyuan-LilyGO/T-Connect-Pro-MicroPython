<!--

 * @Description: None
 * @Author: LILYGO
 * @Date: 2025-05-12 15:13:14
 * @LastEditTime: 2025-05-26 17:40:18
 * @License: GPL 3.0
-->

<h1 align = "center">T-Connect-Pro-MicroPython</h1>

## **English | [中文](./README_CN.md)**

## VersionIteration:
| Version                              | Update date                       |
| :-------------------------------: | :-------------------------------: |
| T-Connect-Pro-Micropython_V1.0        | 2025-05-23               |

## PurchaseLink

| Product                     | SOC           |  FLASH  |  PSRAM   | Link                   |
| :------------------------: | :-----------: |:-------: | :---------: | :------------------: |
| T-Connect-Pro_V1.0   | ESP32S3R8 |   16M   | 8M (Octal SPI) |  [NULL]()   |

## Directory
- [Describe](#describe)
- [Preview](#preview)
- [Module](#module)
- [SoftwareDeployment](#SoftwareDeployment)
- [PinOverview](#pinoverview)
- [RelatedTests](#RelatedTests)
- [FAQ](#faq)
- [Project](#project)

## Describe

T-Connect-Pro is a product based on the ESP32S3 main control chip, consisting of three stacked circuit boards. It features a wide range of functions and is equipped with three different communication modules: CAN, RS485, and RS232, enabling long-distance data transmission. The product includes an Ethernet interface, a relay interface, and a LoRa module (SX1262). It also comes with an LCD screen to facilitate easier operation.

## Preview

### Actual Product Image

## Module

### 1. MCU

* Chip: ESP32-S3-R8
* PSRAM: 8M (Octal SPI) 
* FLASH: 16M
* Related documentation: 
    >[Espressif ESP32-S3 Datasheet](https://www.espressif.com.cn/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

### 2. Screen

<!-- * Size:  -->
* Resolution: 222x480px
* Screen type: TFT、LCD
* Driver chip: ST7796
* Bus communication protocol: Standard SPI

### 3. Touch

* Chip: CST226SE
* Bus communication protocol: IIC

### 4. Lora

* Module: HPD16A

* Chip: SX1262

* Bus communication protocol: Standard SPI

* Related documentation: 
    >[HPD16A_V1.1](./information/HPDTEK_HPD16A_TCXO_V1.1.pdf) <br /> 
    >[SX1262_V2.1](./information/DS_SX1261-2_V2_1.pdf)

### 5. CAN

* Module: TD501MCANFD
* Bus communication protocol: TWAI
* Related documentation: 
    >[TD501MCANFD](./information/TD501MCANFD_MORNSUN.pdf)

### 6. RS485

* module: TD501D485H-A
* Bus communication protocol: UART
* Related documentation: 
    >[TD501D485H-A](./information/TD501D485H-A_K-CUT.pdf)

### 7. RS232

* module: TD501D232H
* Bus communication protocol: UART
* Related documentation: 
    >[TD501D232H](./information/TD501D232H_WJ146289.pdf)

### 8. Ethernet

* Chip: W5500
* Bus communication protocol: Standard SPI
* Related documentation: 
    >[Ethernet_V2.0.0](http://www.arduino.cc/en/Reference/Ethernet)

## SoftwareDeployment

### Examples Support

| Example | `[RT-Thread MicroPython][1.0.11]`<br /> | Description | Picture |
| ------  | ------ | ------ | ------ |
| [CAN](./examples/CAN) | <p align="center">![alt text][supported] | | |
| [CST226SE](./examples/CST226SE) |  <p align="center">![alt text][supported] | | |
| [Ethernet_HTTP](./examples/Ethernet_HTTP) |  <p align="center">![alt text][supported] | | |
| [Ethernet_Relay](./examples/Ethernet_Relay) |  <p align="center">![alt text][supported] | | |
| [Ethernet_Scan](./examples/Ethernet_Scan) |  <p align="center">![alt text][supported] | | |
| [GFX](./examples/GFX) | <p align="center">![alt text][supported] | | |
| [GFX_SX1262](./examples/GFX_SX1262) | <p align="center">![alt text][supported] | | |
| [Original_Test](./examples/Original_Test) | <p align="center">![alt text][supported] | Original factory program | |
| [Relay](./examples/Relay) |  <p align="center">![alt text][supported] | | |
| [RS485](./examples/RS485) | <p align="center">![alt text][supported] | | |
| [RS485_2](./examples/RS485_2) | <p align="center">![alt text][supported] | | |
| [SX126x_PingPong](./examples/SX126x_PingPong) | <p align="center">![alt text][supported] | | |

[supported]: https://img.shields.io/badge/-supported-green "example"

| Firmware | Description | Picture |
| ------  | ------  | ------ |
<<<<<<< HEAD
| [T-Connect-Pro_LVGL_MicroPython_firmware_V1.0](./firmware/T-Connect-Pro_LVGL_MicroPython_firmware_V1.0.bin) |  |  |
=======
| [T-Connect-Pro_LVGL_MicroPython_firmware_V1.0](./firmware/T-Connect-Pro_LVGL_MicroPython_firmware_V1.0.bin) | have lvgl |  |
| [T-Connect-Pro_MicroPython_firmware(import_CAN)_V1.0](./firmware/T-Connect-Pro_MicroPython_firmware(import_CAN)_V1.0.bin) | have CAN | |
>>>>>>> 3022cabafbc62a61a1a4245f348bc481188ef8f3

### RT-Thread MicroPython
1. Install [Python](https://www.python.org/downloads/) (according to you to download the corresponding operating system version, suggest to download version 3.7 or later), MicroPython requirement 3. X version, if you have already installed, you can skip this step).

2. Install[VisualStudioCode](https://code.visualstudio.com/Download),Choose installation based on your system type.

3. Open the "Extension" section of the Visual Studio Code software sidebar(Alternatively, use "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>" to open the extension),Search for the "RT-Thread MicroPython" extension and download it.

4. During the installation of the extension, you can go to GitHub to download the program. You can download the main branch by clicking on the "<> Code" with green text, or you can download the program versions from the "Releases" section in the sidebar.

5. After the installation of the extension is completed, open the Explorer in the sidebar(Alternatively, use "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd>" go open it),Click on "Open Folder," locate the project code you just downloaded (the entire folder), and click "Add." At this point, the project files will be added to your workspace.

6. Open the VisualStudioCode terminal (or use <kbd>Ctrl</kbd>+<kbd>`</kbd>), and enter the command to install the esptools tool.

   ```
   pip install esptools
   ```

7. Erase the flash memory and enter commands in the terminal.

   ```
   python -m esptool --chip esp32s3 --port COMX erase_flash
   ```

   Note：

   1. COMX is the port number. Change it to the port number corresponding to your computer.

8. Upload the MicroPython firmware.

   ```
   python -m esptool --chip esp32s3 --port COMX --baud 460800 --before=default_reset --after=hard_reset write_flash -z 0x0 D:\T-Connect-Pro\firmware\T-Connect-Pro_MicroPython_firmware_V1.0.bin
   ```

   Note：

   1. COMX is the port number. Change it to the port number corresponding to your computer.
   2. D:\T-Connect-Pro\firmware\T-Connect-Pro_MicroPython_firmware_V1.0.bin is the firmware path. Change it to the corresponding storage path.

9. Click on "<kbd>[Device Connected/Disconnected](image/1.png)</kbd>" at the lower left corner, and then click on the pop-up window "<kbd>[COMX](image/2.png)</kbd>" at the top to connect the serial port. A pop-up pops up at the lower right corner saying "<kbd>[Connection successful](image/3.png)</kbd>" and the connection is complete.

10. After opening the code, click on“<kbd>[▶](image/4.png)</kbd>”at the lower left corner to run the program“<kbd>[Run this MicroPython file directly on the device](image/5.png)</kbd>”，Or use the<kbd>Alt</kbd>+<kbd>Q</kbd>），if you want to stop the program, click on the lower left corner of the“<kbd>[⏹](image/6.png)</kbd>”stop running the program.

## PinOverview

| Screen pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| DC         | IO41       |
| SCLK         | IO12       |
| CS         | IO21       |
| BL         | IO46       |

| Touch pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| SDA         | IO39      |
| SCL         | IO40       |
| RST         | IO47      |
| INT         | IO3       |

| Ethernet pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| RST         | IO48       |
| SCLK         | IO12       |
| CS         | IO10       |
| INT         | IO9       |

| Lora pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| RST         | IO42       |
| SCLK         | IO12       |
| CS         | IO14       |
| INT/DIO1         | IO45       |
| BUSY         | IO38       |

| RS485 pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| UART_TX         | IO17       |
| UART_RX         | IO18       |

| RS232 pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| UART_TX         | IO4       |
| UART_RX         | IO5       |

| CAN pins  | ESP32S3 pins|
| :------------------: | :------------------:|
| TWAI_TX         | IO6      |
| TWAI_RX         | IO7       |

## RelatedTests

## FAQ

* Q. Why is my board continuously failing to download the program?
* A. Please hold down the "BOT" key, then press the "RST" key, and use the command again to burn the firmware.

## Project
* [T-Connect-Pro_V1.0](./project/T-Connect-Pro_V1.0.pdf)

