call build_main_bootloader
call build_main
python combine.py mbed-os-example-blinky.bin --app "BUILD_BOOTLOADER/K64F/GCC_ARM/mbed-os-example-blinky.bin,0x00000000" --app "BUILD_MAIN/K64F/GCC_ARM/mbed-os-example-blinky.bin,0x00010000"