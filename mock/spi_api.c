/* mbed Microcontroller Library
 * Copyright (c) 2013 ARM Limited
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
#include "spi_api.h"

void spi_init(spi_t *obj, PinName mosi, PinName miso, PinName sclk, PinName ssel)
{

}

void spi_free(spi_t *obj)
{

}

void spi_format(spi_t *obj, int bits, int mode, int slave)
{

}

void spi_frequency(spi_t *obj, int hz)
{

}

int spi_master_write(spi_t *obj, int value)
{
    return 0;
}


int spi_master_block_write(spi_t *obj, const char *tx_buffer, int tx_length, char *rx_buffer, int rx_length) {
    return 0;
}
