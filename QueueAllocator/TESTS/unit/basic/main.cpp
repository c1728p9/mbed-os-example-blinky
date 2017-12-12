/*
 * Copyright (c) 2013-2016, ARM Limited, All Rights Reserved
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mbed.h"
#include "greentea-client/test_env.h"
#include "unity/unity.h"
#include "utest/utest.h"

#include "QueueAllocator.h"

using namespace utest::v1;
#define TEST_SIZE   64
#define ALIGN_SIZE  sizeof(void*)
#define OVERHEAD    8
#define PAD_VAL     0x55

/**
 * Check if all elements of the array have the expected value
 *
 * @param data array to check
 * @param size size of the array
 * @param value expected value
 * @return true if every element of data is value, false otherwise
 */
static bool same_value(void *data, uint32_t size, uint8_t value)
{
    uint8_t *buf = (uint8_t*)data;
    for (uint32_t i = 0; i < size; i++) {
        if (buf[i] != value) {
            return false;
        }
    }
    return true;
}

/**
 * Test the basic functionality of allocation, enqueue, get and free
 */
void test_case_basic()
{
    QueueAllocator qa(TEST_SIZE);
    for (int i = 0; i < 20; i++) {
        void *data = qa.allocate(i);
        memset(data, PAD_VAL, i);
        qa.enque(data);

        void *new_data = NULL;
        size_t size = 0;
        TEST_ASSERT_TRUE(qa.get(new_data, size));
        TEST_ASSERT_EQUAL(i, size);
        TEST_ASSERT_TRUE(same_value(new_data, i, PAD_VAL));
        qa.free(new_data);

        TEST_ASSERT_FALSE(qa.get(new_data, size));
        TEST_ASSERT_EQUAL(0, new_data);
        TEST_ASSERT_EQUAL(0, size);
    }
}

/**
 * Test the edge case of the biggest allocation
 */
void test_case_big_allocation()
{
    QueueAllocator qa(TEST_SIZE);

    TEST_ASSERT_EQUAL(0, qa.allocate(TEST_SIZE * 2));
    TEST_ASSERT_EQUAL(0, qa.allocate(TEST_SIZE));
    TEST_ASSERT_EQUAL(0, qa.allocate(TEST_SIZE - OVERHEAD - ALIGN_SIZE + 1));
    TEST_ASSERT_NOT_EQUAL(0, qa.allocate(TEST_SIZE - OVERHEAD - ALIGN_SIZE));

    // Further allocations should fail
    TEST_ASSERT_EQUAL(0, qa.allocate(0));
}

/**
 * Test that allocations which aren't ready are handled correctly
 */
void test_case_alloc_not_ready()
{
    QueueAllocator qa(TEST_SIZE);

    void *a = qa.allocate(1);
    TEST_ASSERT_NOT_EQUAL(0, a);
    void *b = qa.allocate(1);
    TEST_ASSERT_NOT_EQUAL(0, b);
    void *c = qa.allocate(1);
    TEST_ASSERT_NOT_EQUAL(0, c);

    void *data = (void*)0;
    size_t size = 0;
    TEST_ASSERT_FALSE(qa.get(data, size));

    // Mark last as ready - Get should return NULL
    qa.enque(c);
    TEST_ASSERT_FALSE(qa.get(data, size));

    // Mark first as ready - Get should return 'a' and then null
    qa.enque(a);
    TEST_ASSERT_TRUE(qa.get(data, size));
    qa.free(data);
    TEST_ASSERT_FALSE(qa.get(data, size));

    // Mark middle as ready - Get should return 'b' then 'c' then null
    qa.enque(b);
    TEST_ASSERT_TRUE(qa.get(data, size));
    qa.free(data);
    TEST_ASSERT_TRUE(qa.get(data, size));
    qa.free(data);
    TEST_ASSERT_FALSE(qa.get(data, size));
}

/**
 * Test that allocations that aren't ready and wrap are handled correctly
 */
void test_case_alloc_not_ready_wrap()
{
    for (int test_size = 0; test_size < 8; test_size++) {

        void *queue[] = {
                NULL, NULL,
                NULL, NULL
        };
        int head = 0;
        int tail = 0;
        int count = sizeof(queue) / sizeof(queue[0]);
        QueueAllocator qa(TEST_SIZE);
        void *data;
        uint32_t size;

        // Add initial entries
        for (int i = 0; i < count - 1; i++) {
            void *tmp = qa.allocate(test_size);
            TEST_ASSERT_NOT_EQUAL(NULL, tmp);
            memset(tmp, PAD_VAL, test_size);
            queue[tail] = tmp;
            tail = (tail + 1) % count;
        }

        // Remove one entry and add another
        for (int i = 0; i < TEST_SIZE  * 4; i++) {
            // Sanity check that no elements are ready
            TEST_ASSERT_EQUAL(false, qa.get(data, size));

            // Mark element as ready then free it
            void *tmp = queue[head];
            qa.enque(tmp);
            head = (head + 1) % count;
            TEST_ASSERT_EQUAL(true, qa.get(data, size));
            TEST_ASSERT_EQUAL(tmp, data);
            TEST_ASSERT_EQUAL(test_size, size);
            TEST_ASSERT_TRUE(same_value(data, size, PAD_VAL));
            qa.free(data);

            // Allocate new element
            tmp = qa.allocate(test_size);
            TEST_ASSERT_NOT_EQUAL(NULL, tmp);
            memset(tmp, PAD_VAL, test_size);
            queue[tail] = tmp;
            tail = (tail + 1) % count;
        }

        // Free remaining entries
        for (int i = 0; i < count - 1; i++) {
            // Mark element as ready then free it
            void *tmp = queue[head];
            qa.enque(tmp);
            head = (head + 1) % count;
            TEST_ASSERT_EQUAL(true, qa.get(data, size));
            TEST_ASSERT_EQUAL(tmp, data);
            TEST_ASSERT_EQUAL(test_size, size);
            TEST_ASSERT_TRUE(same_value(data, size, PAD_VAL));
            qa.free(data);
        }

        TEST_ASSERT_EQUAL(false, qa.get(data, size));
    }
}

/**
 * Test that allocations fail gracefully when there is not space
 */
void test_case_alloc_not_ready_and_fail()
{
    for (int test_size = 0; test_size < 8; test_size++) {

        void *queue[TEST_SIZE / OVERHEAD + 1];
        memset(queue, 0, sizeof(queue));
        int head = 0;
        int tail = 0;
        int count = sizeof(queue) / sizeof(queue[0]);
        QueueAllocator qa(TEST_SIZE);
        void *data;
        uint32_t size;

        uint32_t allocation_count = 0;
        uint32_t free_count = 0;

        for (int i = 0; i < TEST_SIZE  * 4; i++) {

            // Allocate until there is a failure
            void *entry = qa.allocate(test_size);
            while (entry != NULL) {
                memset(entry, PAD_VAL, test_size);
                queue[tail] = entry;
                allocation_count++;
                tail = (tail + 1) % count;
                TEST_ASSERT_NOT_EQUAL(head, tail);
                entry = qa.allocate(test_size);
            }

            // Free one element
            void *tmp = queue[head];
            qa.enque(tmp);
            free_count++;
            head = (head + 1) % count;
            TEST_ASSERT_EQUAL(true, qa.get(data, size));
            TEST_ASSERT_EQUAL(tmp, data);
            TEST_ASSERT_EQUAL(test_size, size);
            TEST_ASSERT_TRUE(same_value(data, size, PAD_VAL));
            qa.free(data);
        }

        TEST_ASSERT(free_count == TEST_SIZE  * 4);
        TEST_ASSERT(allocation_count >= free_count);
    }
}

Case cases[] = {
    Case("Basic functions", test_case_basic),
    Case("Big allocation", test_case_big_allocation),
    Case("Allocation not ready", test_case_alloc_not_ready),
    Case("Allocation not ready wrap", test_case_alloc_not_ready_wrap),
    Case("Allocation not ready and fail", test_case_alloc_not_ready_and_fail)
};

utest::v1::status_t greentea_test_setup(const size_t number_of_cases) {
    GREENTEA_SETUP(5, "default_auto");
    return greentea_test_setup_handler(number_of_cases);
}

Specification specification(greentea_test_setup, cases, greentea_test_teardown_handler);

int main() {
    Harness::run(specification);
}
