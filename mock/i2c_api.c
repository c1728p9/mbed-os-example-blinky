/* mbed Microcontroller Library
 * Copyright (c) 2006-2013 ARM Limited
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

#include "i2c_api.h"

void i2c_init(i2c_t *obj, PinName sda, PinName scl)
{

}

int i2c_start(i2c_t *obj)
{

    return 0;
}

int i2c_stop(i2c_t *obj)
{
    return 0;
}

void i2c_frequency(i2c_t *obj, int hz)
{

}

int i2c_read(i2c_t *obj, int address, char *data, int length, int stop)
{
    return 0;
}

int i2c_write(i2c_t *obj, int address, const char *data, int length, int stop)
{
    return 0;
}

void i2c_reset(i2c_t *obj)
{
    i2c_stop(obj);
}

int i2c_byte_read(i2c_t *obj, int last)
{
    return 0;
}

int i2c_byte_write(i2c_t *obj, int data)
{
    return 0;
}
