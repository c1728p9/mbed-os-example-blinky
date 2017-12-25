/* Copyright (c) 2017 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "ISRSerial.h"
#include "mbed_critical.h"
#include <stdio.h>
#include <cstdarg>

enum ISRFlags {
    DATA_READY = 1 << 0,
    TERMINATE = 1 << 1
};

ISRSerial::ISRSerial(PinName tx, size_t size): SerialBase(tx, NC, MBED_CONF_PLATFORM_DEFAULT_SERIAL_BAUD_RATE), _alloc(size), _error(false)
{
    _thread.start(Callback<void()>(this, &ISRSerial::_main));
}

ISRSerial::~ISRSerial()
{
    _flags.set(TERMINATE);
    _thread.join();
}

int ISRSerial::printf(const char *format, ...) {
    std::va_list arg;
    va_start(arg, format);

    // ARMCC microlib does not properly handle a size of 0.
    // As a workaround supply a dummy buffer with a size of 1.
    char dummy_buf[1];
    int len = vsnprintf(dummy_buf, sizeof(dummy_buf), format, arg);
    if (len < 0) {
        _error = true;
        return len;
    }
    // Make space for null terminating character
    len++;

    core_util_critical_section_enter();
    if (_error) {
        // Don't allow further prints until error is cleared
        core_util_critical_section_exit();
        return 0;
    }
    void *buf = _alloc.allocate(len);
    if (buf == NULL) {
        _error = true;
        core_util_critical_section_exit();
        return 0;
    }
    core_util_critical_section_exit();

    vsnprintf((char*)buf, len, format, arg);

    core_util_critical_section_enter();
    _alloc.enque(buf);
    if (!(_flags.get() & DATA_READY)) {
        // Only set the flag if it isn't already set.
        // This prevents an RTX ISR Queue overflow
        _flags.set(DATA_READY);
    }
    core_util_critical_section_exit();

    va_end(arg);
    return len;
}

void ISRSerial::_main()
{
    while (true) {
        uint32_t flags = _flags.wait_any(DATA_READY | TERMINATE);
        if (flags & DATA_READY) {
            void *data;
            size_t size;
            while (_alloc.get(data, size)) {
                uint8_t *buf = (uint8_t*)data;
                if (size > 0) {
                    // Don't include null terminating character
                    size--;
                }
                for (uint32_t i = 0; i < size; i++) {
                    _base_putc(buf[i]);
                }
                _alloc.free(data);
            }
            if (_error) {
                const char error_msg[] = "\n[overflow]\n";
                const char *pos = error_msg;
                while (*pos) {
                    _base_putc(*pos);
                    pos++;
                }
                _error = false;
            }
        }
        if (flags & TERMINATE) {
            break;
        }
    }
}
