#include "mbed.h"
//#include "USBSerial.h"
#include "USBCDC.h"
#include "ISRSerial.h"

DigitalOut led1(LED1);
//USBSerial serial;
ISRSerial pc(USBTX, 1024 * 4);




// main() runs in its own thread in the OS
int main() {
    pc.printf("Program starting\n");
    USBCDC serial(0x1f00, 0x2012, 0x0001, true);
    while (true) {
        led1 = !led1;
        wait(0.5);
        //serial.writeNB(5, (uint8_t*)"hello", 6, 64);
        //serial.send("hello", 6);
        //const char str[] = "Hello world\n";
        //for (int i = 0; i < sizeof(str) - 1; i++) {
        //    serial.putc(str[i]);
        //}
    }
}

