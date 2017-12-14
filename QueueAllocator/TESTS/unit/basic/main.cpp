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

void test_case_basic()
{
    QueueAllocator qa(64);
    for (int i = 0; i < 20; i++) {
        void *data = qa.allocate(i);
        memset(data, 0x55, i);
        qa.enque(data);

        void *new_data = qa.get();
        TEST_ASSERT_EQUAL(data, new_data);
        qa.free(new_data);
    }
}

void test_case_big_allocation()
{
    QueueAllocator qa(64);

    TEST_ASSERT_EQUAL(0, qa.allocate(100));
    TEST_ASSERT_EQUAL(0, qa.allocate(64));
    TEST_ASSERT_EQUAL(0, qa.allocate(60));
    TEST_ASSERT_EQUAL(0, qa.allocate(56));
    TEST_ASSERT_NOT_EQUAL(0, qa.allocate(55));
}

//void test_case_alloc_not_ready()
//{
//    QueueAllocator qa(64);
//    void *
//}

Case cases[] = {
    Case("Basic functions", test_case_basic),
    Case("Big allocation", test_case_big_allocation),
    //Case("Allocation not ready", test_case_alloc_not_ready),
    //Case("Cleanup memory leak", test_case_memory_leak),


};

utest::v1::status_t greentea_test_setup(const size_t number_of_cases) {
    GREENTEA_SETUP(5, "default_auto");
    return greentea_test_setup_handler(number_of_cases);
}

Specification specification(greentea_test_setup, cases, greentea_test_teardown_handler);

int main() {
    Harness::run(specification);
}
