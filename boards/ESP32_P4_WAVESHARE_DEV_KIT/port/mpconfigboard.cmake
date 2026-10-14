set(IDF_TARGET esp32p4)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.p4_wifi_common
    boards/ESP32_P4_WAVESHARE_DEV_KIT/sdkconfig.p4_waveshare_dev_kit
    boards/ESP32_P4_WAVESHARE_DEV_KIT/sdkconfig.defaults.board
    boards/ESP32_P4_WAVESHARE_DEV_KIT/sdkconfig.board
)

# Keep the first bring-up independent of optional MicroPython submodules.
set(MICROPY_PY_BTREE OFF)
