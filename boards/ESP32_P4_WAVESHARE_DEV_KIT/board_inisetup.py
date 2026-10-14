# SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0

MAIN_PY = """\
# ESP-VISION ESP32_P4_WAVESHARE_DEV_KIT
#
# This board boots into the MicroPython REPL so Thonny, mpremote and WebREPL
# work out of the box; there is no LCD and no EV-MUX console framing.
# Put an application here to run it at startup, or keep this file as the
# no-op default and develop interactively.
print("ESP-VISION ESP32_P4_WAVESHARE_DEV_KIT ready")
"""

README_TXT = """\
ESP-VISION ESP32_P4_WAVESHARE_DEV_KIT

Connect Thonny (interpreter "MicroPython (ESP32)") or mpremote to the board's
UART/USB-Serial-JTAG port and program it like any MicroPython board: the REPL
and the filesystem are plain text, so files can be listed, uploaded and run
directly. main.py runs at startup; boot.py is the place for WiFi setup.
Camera, H.264 and RTSP come from the sensor, h264 and rtsp modules.
"""
