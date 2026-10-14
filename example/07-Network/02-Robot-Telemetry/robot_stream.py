# SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0
#
# Robot demo for the ESP32-P4 Waveshare Dev Kit: streams the camera over RTSP
# while publishing fake robot telemetry (12 servo angles, 3-axis accelerometer,
# 3-axis gyroscope and a fused yaw/pitch/roll attitude) as UDP datagrams.
#
# Run from Thonny, or from a host with:
#   mpremote connect COM3 run example/07-Network/02-Robot-Telemetry/robot_stream.py
#
# WiFi credentials are read from /wifi.py on the board:
#   SSID = "my-network"
#   PASSWORD = "my-password"
# Keeping them in /wifi.py (not in this file) is what lets this example be
# shared without leaking them.
#
# Wire format (little-endian, 52 bytes, struct "<2sII12H3h3h3h"):
#   offset  type        field
#   0       2s          magic b"EV"
#   2       uint32      sequence number
#   6       uint32      uptime in ms
#   10      12 x u16    servo angles, 0.1 deg units (0..1800 == 0..180 deg)
#   34      3 x int16   accelerometer, mg
#   40      3 x int16   gyroscope, 0.1 deg/s
#   46      3 x int16   fused yaw/pitch/roll, 0.1 deg
#
# BLE: this firmware cannot expose BLE, so the telemetry goes over UDP here.
# The ESP32-P4 has no radio and the board header disables MICROPY_PY_BLUETOOTH;
# BLE would have to come from the on-board ESP32-C6 through esp_hosted's
# virtual HCI, which MicroPython's bluetooth module does not drive. The payload
# above is transport-agnostic, so a BLE build could publish the same bytes with
# this GATT layout (advertised as "ESP-VISION Robot"):
#
#   Service  ROBOT_TELEMETRY  12345678-1234-5678-1234-56789abcdef0
#     char   TELEMETRY  ...f1  notify, 52 B   the packet above, at ~20 Hz
#     char   SERVOS     ...f2  read,   24 B   12 x uint16, 0.1 deg
#     char   ATTITUDE   ...f3  read,    6 B   yaw/pitch/roll, 0.1 deg
#     char   COMMAND    ...f4  write,  24 B   host -> 12 x uint16 setpoints

import math
import network
import socket
import struct
import time

import sensor
import h264
import rtsp

try:
    import wifi

    SSID, PASSWORD = wifi.SSID, wifi.PASSWORD
except ImportError:
    SSID, PASSWORD = "your-ssid", "your-password"

WIDTH, HEIGHT, FPS = 320, 240, 30
BITRATE, GOP = 2_000_000, 10
RTSP_PORT = 8554

TELEMETRY_PORT = 5005
TELEMETRY_PERIOD_MS = 50
JSON_EVERY = 20
SERVO_COUNT = 12

# The ISP white-balance block ships disabled on this camera path, which leaves a
# green cast; a few damped gray-world steps over real pixel values fix it.
WHITE_BALANCE = True

TELEMETRY_FORMAT = "<2sII12H3h3h3h"
TELEMETRY_MAGIC = b"EV"
TELEMETRY_SIZE = struct.calcsize(TELEMETRY_FORMAT)


def broadcast_address(ip, mask):
    parts = [int(p) for p in ip.split(".")]
    netmask = [int(p) for p in mask.split(".")]
    return ".".join(str(p | (~m & 0xFF)) for p, m in zip(parts, netmask))


def sample_means(img):
    r = g = b = 0.0
    n = 0
    for x in range(10, WIDTH - 10, 40):
        for y in range(10, HEIGHT - 10, 40):
            pr, pg, pb = img.get_pixel(x, y)
            r += pr
            g += pg
            b += pb
            n += 1
    return (r / n, g / n, b / n)


def calibrate_white_balance():
    sensor.set_ipa(False)
    wb = sensor.get_isp("wb") or {}
    rg = float(wb.get("rg", 1.0))
    bg = float(wb.get("bg", 1.0))
    for _ in range(4):
        r, g, b = sample_means(sensor.snapshot())
        if r <= 0 or b <= 0:
            break
        rg = max(0.8, min(2.5, rg * (g / r) ** 0.5))
        bg = max(0.8, min(2.5, bg * (g / b) ** 0.5))
        sensor.set_isp("wb", enable=True, rg=round(rg, 3), bg=round(bg, 3))
        sensor.skip_frames(n=8)
    print("white balance rg=%.2f bg=%.2f" % (rg, bg))


class FakeSensors:
    """Plausible-looking servo and IMU data, with a real complementary filter."""

    def __init__(self, servo_count):
        self.servo_count = servo_count
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.last_ms = time.ticks_ms()

    def read(self, now_ms):
        t = time.ticks_diff(now_ms, self.last_ms) / 1000.0
        self.last_ms = now_ms
        if t <= 0 or t > 1.0:
            t = 0.02
        uptime = time.ticks_ms() / 1000.0

        # A walking gait: every joint swings with its own phase and rate.
        servos = []
        for i in range(self.servo_count):
            phase = (i % 4) * (math.pi / 2)
            rate = 0.5 + 0.25 * (i % 3)
            angle = 90.0 + 60.0 * math.sin(2 * math.pi * rate * uptime + phase)
            servos.append(int(max(0.0, min(180.0, angle)) * 10))

        # Accelerometer: gravity on Z plus the gait's sway (mg).
        ax = 60.0 * math.sin(2 * math.pi * 0.6 * uptime)
        ay = 45.0 * math.cos(2 * math.pi * 0.5 * uptime)
        az = 1000.0 + 35.0 * math.sin(2 * math.pi * 1.2 * uptime)

        # Gyroscope: the body rates that would produce that sway (0.1 deg/s).
        gx = 120.0 * math.sin(2 * math.pi * 0.5 * uptime) + 4.0
        gy = 90.0 * math.cos(2 * math.pi * 0.6 * uptime) - 3.0
        gz = 70.0 * math.sin(2 * math.pi * 0.2 * uptime) + 2.0

        # Fused attitude: tilt from the accelerometer, heading from gyro Z with a
        # slow leak towards zero so the fake heading does not walk away.
        accel_pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
        accel_roll = math.degrees(math.atan2(ay, az))
        self.pitch += (accel_pitch - self.pitch) * 0.1
        self.roll += (accel_roll - self.roll) * 0.1
        self.yaw = (self.yaw + (gz / 10.0) * t) * 0.999
        if self.yaw > 180.0:
            self.yaw -= 360.0

        return (
            servos,
            (int(ax), int(ay), int(az)),
            (int(gx), int(gy), int(gz)),
            (int(self.yaw * 10), int(self.pitch * 10), int(self.roll * 10)),
        )


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=network.WLAN.PM_NONE)  # no radio power save: lower jitter
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
    for _ in range(150):
        if wlan.isconnected():
            break
        time.sleep_ms(100)
    if not wlan.isconnected():
        raise OSError("wifi connect failed (is /wifi.py correct?), status=%s" % wlan.status())
    return wlan


def main():
    wlan = connect_wifi()
    ip, mask, _gateway, _dns = wlan.ifconfig()
    telemetry_host = broadcast_address(ip, mask)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("RTSP      rtsp://%s:%d/" % (ip, RTSP_PORT))
    print("telemetry udp://%s:%d (%d bytes/packet)" % (telemetry_host, TELEMETRY_PORT, TELEMETRY_SIZE))

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=1000)
    if WHITE_BALANCE:
        calibrate_white_balance()

    encoder = h264.H264Encoder(WIDTH, HEIGHT, fps=FPS, gop=GOP, bitrate=BITRATE, qp_max=30)
    server = rtsp.RTSPServer(WIDTH, HEIGHT, fps=FPS, listen_port=RTSP_PORT)

    sensors = FakeSensors(SERVO_COUNT)
    sequence = 0
    next_tx = time.ticks_ms()

    try:
        while True:
            img = sensor.snapshot()
            server.send(encoder.encode(img))

            now = time.ticks_ms()
            if time.ticks_diff(now, next_tx) >= 0:
                next_tx = time.ticks_add(now, TELEMETRY_PERIOD_MS)
                sequence += 1
                servos, accel, gyro, attitude = sensors.read(now)
                packet = struct.pack(
                    TELEMETRY_FORMAT,
                    TELEMETRY_MAGIC,
                    sequence,
                    now,
                    *servos,
                    *accel,
                    *gyro,
                    *attitude,
                )
                try:
                    sender.sendto(packet, (telemetry_host, TELEMETRY_PORT))
                except OSError:
                    pass  # nobody listening is not an error for UDP broadcast
                if sequence % JSON_EVERY == 0:
                    print(
                        '{"seq":%d,"servo0..3":%s,"accel":%s,"gyro":%s,"att":%s}'
                        % (sequence, servos[:4], accel, gyro, attitude)
                    )
    finally:
        server.stop()
        encoder.close()
        sender.close()
        sensor.shutdown()
        print("stopped")


main()
