# SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0

MAIN_PY = """\
import sensor
import time

print("ESP-VISION ESP32_P4_WAVESHARE_DEV_KIT ready")

try:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=1000)

    while True:
        img = sensor.snapshot()
        img.flush()
        time.sleep_ms(20)
finally:
    sensor.shutdown()
"""

README_TXT = """\
ESP-VISION ESP32_P4_WAVESHARE_DEV_KIT

Edit main.py to run your Python vision script.
Use the ESP-VISION VSCode extension to run scripts and preview frames.
The default main.py captures QVGA frames and flushes them to the host
preview, because this board has no LCD.
"""
