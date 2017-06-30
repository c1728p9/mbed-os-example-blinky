// The 'features' section in 'target.json' is now used to create the device's hardware preprocessor switches.
// Check the 'features' section of the target description in 'targets.json' for more details.
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
#ifndef MBED_DEVICE_H
#define MBED_DEVICE_H

#include "PinNames.h"
#include <stdint.h>
#include "cmsis.h"

#include "PortNames.h"

typedef struct {
    char dummy;
} gpio_t;

struct gpio_irq_s {
    char dummy;
};

struct port_s {
    char dummy;
};

struct pwmout_s {
    char dummy;
};

struct serial_s {
    char dummy;
};

struct analogin_s {
    char dummy;
};

struct i2c_s {
    char dummy;
};

struct spi_s {
    char dummy;
};

struct dac_s {
    char dummy;
};

struct trng_s {
    char dummy;
};

#define LED1 (PinName)1

#endif
