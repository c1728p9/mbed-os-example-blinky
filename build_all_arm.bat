mbed compile -j0 -t ARM -m K64F --build BUILD_BOOTLOADER/K64F/ARM -DENTRY_POINT=main_bootloader -DMAIN_ADDR=0x10000 -l custom\MK64FN1M0xxx12_bootloader.sct
mbed compile -j0 -t ARM -m K64F --build BUILD_MAIN//K64F/ARM -DMAIN_ADDR=0x10000 -l custom\MK64FN1M0xxx12_application.sct
python combine.py mbed-os-example-blinky.bin --app "BUILD_BOOTLOADER/K64F/ARM/mbed-os-example-blinky.bin,0x00000000" --app "BUILD_MAIN/K64F/ARM/mbed-os-example-blinky.bin,0x00010000"

