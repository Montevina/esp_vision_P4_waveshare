#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0
#
# Decode the robot telemetry that robot_stream.py broadcasts over UDP.
#
#   python host_listener.py [port]        (default port 5005)
#
# The board broadcasts to its subnet broadcast address, so any host on the same
# network sees the packets without configuring addresses.

import socket
import struct
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5005
FORMAT = "<2sII12H3h3h3h"
SIZE = struct.calcsize(FORMAT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))
print("listening on udp/%d ... (Ctrl-C to stop)" % PORT)

window_start = time.monotonic()
received = 0

while True:
    data, address = sock.recvfrom(2048)
    if len(data) < SIZE:
        continue
    fields = struct.unpack(FORMAT, data[:SIZE])
    magic, sequence, uptime_ms = fields[0], fields[1], fields[2]
    if magic != b"EV":
        continue
    servos = fields[3:15]
    accel = fields[15:18]
    gyro = fields[18:21]
    attitude = fields[21:24]

    received += 1
    now = time.monotonic()
    if now - window_start < 0.5:
        continue
    rate = received / (now - window_start)
    received = 0
    window_start = now

    print("%s seq=%d uptime=%.1fs  %.1f Hz  (%d bytes)" % (address[0], sequence, uptime_ms / 1000.0, rate, len(data)))
    print("  servos   " + " ".join("%5.1f" % (value / 10.0) for value in servos))
    print("  accel    x=%7.1f y=%7.1f z=%7.1f  mg" % accel)
    print("  gyro     x=%7.1f y=%7.1f z=%7.1f  deg/s" % gyro)
    print("  attitude yaw=%7.1f pitch=%7.1f roll=%7.1f  deg" % attitude)
