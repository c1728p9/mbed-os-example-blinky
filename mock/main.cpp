#include "mbed.h"

//DigitalOut led1(LED1);

// main() runs in its own thread in the OS
int main() {
    printf("Hello world 2\r\n");
    while (true) {
        //led1 = !led1;
        wait(0.5);
    }
}

//extern "C"{
//
///**
// * @brief Retarget of exit for GCC.
// * @details Unlike the standard version, this function doesn't call any function
// * registered with atexit before calling _exit.
// */
//void __wrap_exit(int return_code) {
//    _exit(return_code);
//}
//
//}

//void *operator new(std::size_t count)
//{
//    void *buffer = malloc(count);
//    if (NULL == buffer) {
//        exit(-1);
//        //error("Operator new out of memory\r\n");
//    }
//    return buffer;
//}
//
//void *operator new[](std::size_t count)
//{
//    void *buffer = malloc(count);
//    if (NULL == buffer) {
//        exit(-1);
//        //error("Operator new[] out of memory\r\n");
//    }
//    return buffer;
//}
//
//void operator delete(void *ptr)
//{
//    if (ptr != NULL) {
//        free(ptr);
//    }
//}
//void operator delete[](void *ptr)
//{
//    if (ptr != NULL) {
//        free(ptr);
//    }
//}

extern "C" void core_util_critical_section_enter(void)
{

}

/** Mark the end of a critical section
  *
  * This function should be called to mark the end of a critical section of code.
  * @note
  * NOTES:
  * 1) The use of this style of critical section is targetted at C based implementations.
  * 2) These critical sections can be nested.
  * 3) The interrupt enable state on entry to the first critical section (of a nested set, or single
  *    section) will be preserved on exit from the section.
  * 4) This implementation will currently only work on code running in privileged mode.
  */
extern "C" void core_util_critical_section_exit(void)
{

}

extern "C" void mbed_die()
{

}

