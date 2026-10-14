/*
 * SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef ESP_VISION_BOARD_CONFIG_H
#define ESP_VISION_BOARD_CONFIG_H

#define ESP_VISION_BOARD_ARCH                  "ESP32P4"
#define ESP_VISION_BOARD_TYPE                  "ESP32_P4_WAVESHARE_DEV_KIT"
#define ESP_VISION_PORT_ESP32                       (1)

/* This board is meant for plain-REPL MicroPython tooling (Thonny, mpremote,
 * WebREPL), so the console is not framed by EV-MUX at boot. The ESP-VISION
 * host tooling can still be enrolled at runtime with sensor.evmux(True). */
#define ESP_VISION_EV_MUX_DEFAULT_ENABLED           (0)

#define ESP_VISION_IMLIB_PROFILER_ENABLE            (0)
#define ESP_VISION_IMLIB_GPU_ENABLE                 (0)
#define ESP_VISION_IMLIB_JPEG_CODEC_ENABLE          (0)

#define ESP_VISION_CACHE_LINE_SIZE                  (32)
#define ESP_VISION_ALLOC_ALIGNMENT                  (ESP_VISION_CACHE_LINE_SIZE)
#define ESP_VISION_DMA_ALIGNMENT                    (ESP_VISION_CACHE_LINE_SIZE)

#define ESP_VISION_JPEG_QUALITY_LOW                 (60)
#define ESP_VISION_JPEG_QUALITY_HIGH                (60)
#define ESP_VISION_JPEG_QUALITY_THRESHOLD           (320 * 240 * 2)

/* Camera configuration. */
#define ESP_VISION_CAMERA_SENSOR_ID                 (0x5647)
#define ESP_VISION_CAMERA_RAW_INPUT_WIDTH           (1280)
#define ESP_VISION_CAMERA_RAW_INPUT_HEIGHT          (960)
#define ESP_VISION_CAMERA_ACTIVE_INPUT_WIDTH        (640)
#define ESP_VISION_CAMERA_ACTIVE_INPUT_HEIGHT       (480)
#define ESP_VISION_CAMERA_PPA_OUTPUT_QQVGA_WIDTH    (160)
#define ESP_VISION_CAMERA_PPA_OUTPUT_QQVGA_HEIGHT   (120)
#define ESP_VISION_CAMERA_PPA_OUTPUT_QVGA_WIDTH     (320)
#define ESP_VISION_CAMERA_PPA_OUTPUT_QVGA_HEIGHT    (240)
#define ESP_VISION_CAMERA_PPA_OUTPUT_VGA_WIDTH      (640)
#define ESP_VISION_CAMERA_PPA_OUTPUT_VGA_HEIGHT     (480)
#define ESP_VISION_CAMERA_BUFFER_COUNT              (2)
#define ESP_VISION_CAMERA_SCCB_I2C_PORT             (0)
#define ESP_VISION_CAMERA_SCCB_I2C_SCL_PIN          (8)
#define ESP_VISION_CAMERA_SCCB_I2C_SDA_PIN          (7)
/* The OV5647 module on this board is a free-running Raspberry Pi style
 * MIPI-CSI camera: reset, power-down and XCLK are not wired to the SoC. */
#define ESP_VISION_CAMERA_SENSOR_RESET_PIN          (-1)
#define ESP_VISION_CAMERA_SENSOR_PWDN_PIN           (-1)
#define ESP_VISION_CAMERA_XCLK_PIN                  (-1)
#define ESP_VISION_CAMERA_SCCB_I2C_FREQ             (100000)
#define ESP_VISION_CAMERA_XCLK_FREQ                 (0)

/* SD card configuration. */
#define ESP_VISION_SDCARD_MOUNT_PATH                "/sdcard"
#define ESP_VISION_SDCARD_SLOT                      (0)
#define ESP_VISION_SDCARD_BUS_WIDTH                 (4)
/* No enable or card-detect GPIO is wired on this board. */
#define ESP_VISION_SDCARD_EN_PIN                    (-1)
#define ESP_VISION_SDCARD_EN_ACTIVE_LEVEL           (0)
#define ESP_VISION_SDCARD_DETECT_PIN                (-1)
#define ESP_VISION_SDCARD_DETECT_PRESENT_LEVEL      (0)
#define ESP_VISION_SDCARD_LDO_CHAN_ID               (4)

#endif /* ESP_VISION_BOARD_CONFIG_H */
