mbed compile -j0 -t IAR -m K64F --profile custom/default_bootloader.json --build BUILD_BOOTLOADER/K64F/IAR -DENTRY_POINT=main_bootloader -DMAIN_ADDR=0x10000 -l custom/MK64FN1M0xxx12_bootloader.icf
mbed compile -j0 -t IAR -m K64F --build BUILD_MAIN/K64F/IAR -DMAIN_ADDR=0x10000 -l custom/MK64FN1M0xxx12_application.icf
python combine.py mbed-os-example-blinky.bin --app "BUILD_BOOTLOADER/K64F/IAR/mbed-os-example-blinky.bin,0x00000000" --app "BUILD_MAIN/K64F/IAR/mbed-os-example-blinky.bin,0x00010000"

