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
#include "QueueAllocator.h"

enum entry_state_t {
    ENTRY_ALLOCATED,
    ENTRY_READY,
    ENTRY_SKIP
};

struct buffer_entry_t {
    uint32_t size;
    entry_state_t state;
};
static const uint32_t align = sizeof(void*);

static void *write_entry(uint8_t *buf, uint32_t pos, uint32_t size, entry_state_t state)
{
    buffer_entry_t *entry = (buffer_entry_t*)(buf + pos);
    entry->size = size;
    entry->state = state;
    return (void*)(entry + 1);
}

static uint32_t align_up(uint32_t value)
{
    uint32_t remainder = value % align;
    if (remainder) {
        value = value + (align - remainder);
    }
    return value;
}

QueueAllocator::QueueAllocator(uint32_t size)
    : _buf(NULL), _size(size), _head(0), _tail(0), _error(false)
{
    _buf = new uint8_t[size]();
}

QueueAllocator::~QueueAllocator()
{
    delete[] _buf;
    _buf = NULL;
}

void *QueueAllocator::allocate(uint32_t size)
{
    uint32_t total_size = size + sizeof(buffer_entry_t);
    uint32_t head = _head;
    uint32_t tail = _tail;

    if (tail >= head) {
        uint32_t free_bytes = (head + _size) - tail - align;
        if (total_size > free_bytes) {
            // Not enough free space
            _error = true;
            return NULL;
        }

        uint32_t free_end = _size - tail;
        if (total_size <= free_end) {
            _tail = align_up(tail + total_size);
            if (_tail >= _size) {
                _tail = 0;
            }
            return write_entry(_buf, tail, size, ENTRY_ALLOCATED);
        }

        // Insert dummy node and fall through
        write_entry(_buf, tail, _size - tail - sizeof(buffer_entry_t), ENTRY_SKIP);
        tail = 0;
    }

    // One free region
    uint32_t free_middle = tail - head - align;
    if (total_size <= free_middle) {
        _tail = align_up(tail + total_size);
        return write_entry(_buf, tail, size, ENTRY_ALLOCATED);
    }

    _error = true;
    return NULL;
}

void QueueAllocator::enque(void *allocation)
{
    buffer_entry_t *entry = (buffer_entry_t*)allocation - 1;
    MBED_ASSERT(entry->state == ENTRY_ALLOCATED);
    entry->state = ENTRY_READY;
}

void *QueueAllocator::get()
{
    if (_head == _tail) {
        return NULL;
    }
    buffer_entry_t *entry = (buffer_entry_t*)(_buf + _head);
    if (entry->state == ENTRY_SKIP) {
        free((void*)(entry + 1));
        entry = (buffer_entry_t*)(_buf + _head);
    }

    if (entry->state != ENTRY_READY) {
        return NULL;
    }

    return (void*)(entry + 1);
}

void QueueAllocator::free(void *allocation)
{
    buffer_entry_t *entry = (buffer_entry_t*)allocation - 1;
    MBED_ASSERT((void*)entry == (void*)(_buf + _head));
    do {
        _head = align_up(_head + entry->size + sizeof(buffer_entry_t));
        if (_head >= _size) {
            _head = 0;
        }
        entry = (buffer_entry_t *)(_buf + _head);
    } while ((_head != _tail) && (entry->state == ENTRY_SKIP));
}

