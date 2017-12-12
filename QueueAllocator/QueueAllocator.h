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
#ifndef QUEUE_ALLOCATOR_H
#define QUEUE_ALLOCATOR_H

#include "mbed.h"

class QueueAllocator {
public:
    QueueAllocator(size_t size);
    ~QueueAllocator();

    /**
     * Allocate a segment of memory of size bytes
     *
     * @param size size of allocation in bytes
     * @return allocated memory or NULL if there is no free memory
     */
    void *allocate(size_t size);

    /**
     * Enqueue the allocation onto the queue
     *
     * @param allocation entry to enqueue
     * @note The allocation must have been allocated from QueueAllocator::allocate
     */
    void enque(void *allocation);

    /**
     * Get the allocation at the front of the list
     *
     * @param data pointer to fill
     * @param size variable to store the size of data to
     * @return true if entry was retrieved, false otherwise
     */
    bool get(void *&data, size_t &size);

    /**
     * Free entry returned by get
     *
     * @param allocation Allocation to free
     */
    void free(void *allocation);

protected:
    uint8_t *_buf;
    size_t _size;
    size_t _head;
    size_t _tail;
    bool _error;
};

#endif
