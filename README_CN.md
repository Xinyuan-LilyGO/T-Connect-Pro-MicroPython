<!--

 * @Description: None
 * @Author: LILYGO
 * @Date: 2025-05-12 15:13:14
 * @LastEditTime: 2025-05-17 17:40:18
 * @License: GPL 3.0
-->
<<<<<<< HEAD
<h1 align = "center">T-Connect-Pro-Micropython</h1>
=======
<h1 align = "center">T-Connect-Pro-MicroPython</h1>
>>>>>>> 82810ddefc4e5683de1dbf1cc8fb486c608ea16f

## **[English](./README.md) | 中文**

## 版本迭代:
| Version                               | Update date                       |
| :-------------------------------: | :-------------------------------: |
| T-Connect-Pro-Micropython_V1.0          | 2025-05-17                    |

## 购买链接

| Product                     | SOC           |  FLASH  |  PSRAM   | Link                   |
| :------------------------: | :-----------: |:-------: | :---------: | :------------------: |
| T-Connect-Pro_V1.0   | ESP32S3R8 |   16M   | 8M (Octal SPI) |  [NULL]()   |

## 目录
- [描述](#描述)
- [预览](#预览)
- [模块](#模块)
- [软件部署](#软件部署)
- [引脚总览](#引脚总览)
- [相关测试](#相关测试)
- [常见问题](#常见问题)
- [项目](#项目)

## 描述

T-Connect-Pro基于主控芯片ESP32S3，由3层板子堆叠组合而成的产品，功能丰富多样，板载3种不同通信模块：CAN、RS485、RS232实现远距离传输，拥有一个以太网接口、一个继电器接口、一个Lora模块（SX1262），配备LCD屏幕使得操作更加便捷。

## 预览

### 实物图

## 模块

### 1. MCU

* 芯片：ESP32-S3-R8
* PSRAM：8M (Octal SPI) 
* FLASH：16M
* 相关资料：
    >[Espressif ESP32-S3 Datasheet](https://www.espressif.com.cn/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

### 2. 屏幕

<!-- * 尺寸：英寸LCD屏幕 -->

* 分辨率：222x480px
* 屏幕类型：TFT、LCD
* 驱动芯片：ST7796
* 总线通信协议：标准SPI

### 3. 触摸

* 芯片：CST226SE
* 总线通信协议：IIC

### 4. Lora

* 模块：HPD16A

* 芯片：SX1262

* 使用总线通信协议：标准SPI

* 相关资料：
    >[HPD16A_V1.1](./information/HPDTEK_HPD16A_TCXO_V1.1.pdf)  <br /> 
    >[SX1262_V2.1](./information/DS_SX1261-2_V2_1.pdf)

### 5. CAN

* 模块：TD501MCANFD
* 使用总线通信协议：TWAI
* 相关资料：
    >[TD501MCANFD](./information/TD501MCANFD_MORNSUN.pdf)

### 6. RS485

* 模块：TD501D485H-A
* 使用总线通信协议：UART
* 相关资料：
    >[TD501D485H-A](./information/TD501D485H-A_K-CUT.pdf)

### 7. RS232

* 模块：TD501D232H
* 使用总线通信协议：UART
* 相关资料：
    >[TD501D232H](./information/TD501D232H_WJ146289.pdf)

### 8. 以太网

* 芯片：W5500
* 使用总线通信协议：标准SPI

## 软件部署

### 示例支持

| Example | `[RT-Thread MicroPython][1.0.11]`<br /> | Description | Picture |
| ------  | ------ | ------ | ------ |
| [CAN](./examples/CAN) | <p align="center">![alt text][supported] | | |
| [CST226SE](./examples/CST226SE) |  <p align="center">![alt text][supported] | | |
| [Ethernet_HTTP](./examples/Ethernet_HTTP) |  <p align="center">![alt text][supported] | | |
| [Ethernet_Relay](./examples/Ethernet_Relay) |  <p align="center">![alt text][supported] | | |
| [Ethernet_Scan](./examples/Ethernet_Scan) |  <p align="center">![alt text][supported] | | |
| [GFX](./examples/GFX) | <p align="center">![alt text][supported] | | |
| [GFX_SX1262](./examples/GFX_SX1262) |   | | |
| [Original_Test](./examples/Original_Test) |   | 出厂程序 | |
| [Relay](./examples/Relay) |  <p align="center">![alt text][supported] | | |
| [RS485](./examples/RS485) | <p align="center">![alt text][supported] | | |
| [RS485_2](./examples/RS485_2) | <p align="center">![alt text][supported] | | |
| [SX126x_PingPong](./examples/SX126x_PingPong) | <p align="center">![alt text][supported] | | |

[supported]: https://img.shields.io/badge/-supported-green "example"

| Firmware | Description | Picture |
| ------  | ------  | ------ |
| [T-Connect-Pro_LVGL_MicroPython_firmware_V1.0](./firmware/T-Connect-Pro_LVGL_MicroPython_firmware_V1.0.bin) | 带LVGL库 |  |
| [T-Connect-Pro_MicroPython_firmware(import_CAN)_V1.0](./firmware/T-Connect-Pro_MicroPython_firmware(import_CAN)_V1.0.bin) | 带CAN库 | |

### RT-Thread MicroPython
1. 安装[Python](https://www.python.org/downloads/)（根据你操作系统下载相应的版本即可，建议下载3.7或以后的版本即可），MicroPython要求3.x的版本，如果已经安装，可以跳过此步骤）。

2. 安装[VisualStudioCode](https://code.visualstudio.com/Download)，根据你的系统类型选择安装。

3. 打开VisualStudioCode软件侧边栏的“扩展”（或者使用<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>打开扩展），搜索“RT-Thread MicroPython”扩展并下载。

4. 在安装扩展的期间，你可以前往GitHub下载程序，你可以通过点击带绿色字样的“<> Code”下载主分支程序，也通过侧边栏下载“Releases”版本程序。

5. 扩展安装完成后，打开侧边栏的资源管理器（或者使用<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd>打开），点击“打开文件夹”，找到刚刚你下载的项目代码（整个文件夹），点击“添加”，此时项目文件就添加到你的工作区了。

6. 打开VisualStudioCode终端（或者使用<kbd>Ctrl</kbd>+<kbd>`</kbd>），输入命令安装esptools工具。

   ```
   pip install esptools
   ```

7. 擦除闪存，在终端输命令。

   ```
   python -m esptool --chip esp32s3 --port COMX erase_flash
   ```

   注意：

   1. COMX为端口号，更改为电脑对应的端口号。

8. 上传MicroPython固件。

   ```
   python -m esptool --chip esp32s3 --port COMX --baud 460800 --before=default_reset --after=hard_reset write_flash -z 0x0 D:\T-Connect-Pro\firmware\T-Connect-Pro_MicroPython_firmware_V1.0.bin
   ```

   注意：

   1. COMX为端口号，更改为电脑对应的端口号。
   2. D:\T-Connect-Pro\firmware\T-Connect-Pro_MicroPython_firmware_V1.0.bin为固件路径，更改为对应存放路径。

9. 点击左下角的“<kbd>[设备连接/断开](image/1.png)</kbd>”，然后点击上方弹出的窗口“<kbd>[COMX](image/2.png)</kbd>”进行串口连接，右下角弹出“<kbd>[连接成功](image/3.png)</kbd>”及连接完成。

10. 打开代码后，点击左下角的“<kbd>[▶](image/4.png)</kbd>”运行程序（或者在代码处点击鼠标右键选择“<kbd>[直接在设备上运行该MIC肉Python文件](image/5.png)</kbd>”，或者使用<kbd>Alt</kbd>+<kbd>Q</kbd>），如果要停止程序则点击左下角的“<kbd>[⏹](image/6.png)</kbd>”停止运行程序。

## 引脚总览

| 屏幕引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| DC         | IO41       |
| SCLK         | IO12       |
| CS         | IO21       |
| BL         | IO46       |

| 触摸引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| SDA         | IO39      |
| SCL         | IO40       |
| RST         | IO47      |
| INT         | IO3       |

| 以太网引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| RST         | IO48       |
| SCLK         | IO12       |
| CS         | IO10       |
| INT         | IO9       |

| Lora引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| MOSI         | IO11       |
| MISO         | IO13       |
| RST         | IO42       |
| SCLK         | IO12       |
| CS         | IO14       |
| INT/DIO1         | IO45       |
| BUSY         | IO38       |

| RS485引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| UART_TX         | IO17       |
| UART_RX         | IO18       |

| RS232引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| UART_TX         | IO4       |
| UART_RX         | IO5       |

| CAN引脚  | ESP32S3引脚|
| :------------------: | :------------------:|
| TWAI_TX         | IO6      |
| TWAI_RX         | IO7       |

## 相关测试

## 常见问题

* Q. 为什么我的板子一直烧录固件失败呢？
* A. 请按住"BOT"按键，再按下"RST"按键，重新使用命令烧录固件。

## 项目
* [T-Connect-Pro_V1.0](./project/T-Connect-Pro_V1.0.pdf)
