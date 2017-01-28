#include "mbed.h"

//class ExampleClass {
//public:
//    ExampleClass() {
//        printf("This code can ran before main\r\n");
//        wait(2);
//    }
//};
//
//void second_main(const void* arg)
//{
//    while (true) {
//        wait(1);
//        printf("main 2\r\n");
//    }
//}
//
DigitalOut led1(LED1);
//
//// Thread will start executing before main is called
//Thread thread(Callback<void()>(second_main, (const void*)0));
//
//// The constructor of ec will get called before main starts
//ExampleClass ec;
//
//


int main() {
    //mbed_application_start(0);
    while (true) {
        printf("main 1.1\r\n");
        led1 = !led1;
        wait(0.5);
    }
}

int main_bootloader()
{
    int i;
    for (i = 0; i < 3; i++) {
        printf("main 2.1\r\n");
        led1 = !led1;
        wait(0.5);
    }
    mbed_application_start(MAIN_ADDR);
}
