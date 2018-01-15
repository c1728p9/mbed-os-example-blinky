"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function

from mbed_host_tests import BaseHostTest
from argparse import ArgumentParser
import time
import sys

import usb.core
try:
    from usb_cdc import USBCdc
except Exception as e:
    print("Error %s" % e)

class PyusbBasicTest(BaseHostTest):
    """
    """
    def _callback_usb_enumeration_done(self, key, value, timestamp):
        print("Received key %s = %s" % (key, value))
        self.log("Received key %s = %s" % (key, value))
        test_device(value, self.log)

    def setup(self):
        self.__result = False
        self.register_callback('usb_enumeration_done', self._callback_usb_enumeration_done)
        print("Setup host test!!!!")

    def result(self):
        return self.__result

    def teardown(self):
        pass


def test_device(serial_number, log=print):
        dev = usb.core.find(serial_number=serial_number)
        if dev is None:
            log("Device not found")
            return

        print("Default timeout %s" % dev.default_timeout)
        dev.default_timeout = 5000

        cdc = USBCdc(dev)
        cdc.lock()
        cdc.write("Hello world")
        cdc.get_line_coding()
        cdc.set_line_coding(9600)
        #cdc.get_line_coding()

        cdc.unlock()

        # Control OUT stall
        try:
            request_type = 0x40                         # Host-to-device, Vendor request to Device
            request = 0x20                              # Nonsense request
            value = 0                                   # Always 0 for this request
            index = 0                                   # Communication interface
            data = bytearray(64)                        # Dummy data
            dev.ctrl_transfer(request_type, request, value, index, data, 5000)
            log("Invalid request not stalled")
        except usb.core.USBError:
            log("Invalid request stalled")

        # Control request with no data stage (Device-to-host)
        try:
            request_type = 0xC0                         # Device-to-host, Vendor request to Device
            request = 0x20                              # Nonsense request
            value = 0                                   # Always 0 for this request
            index = 0                                   # Communication interface
            length = 0
            dev.ctrl_transfer(request_type, request, value, index, length, 5000)
            log("Invalid request not stalled")
        except usb.core.USBError:
            log("Invalid request stalled")

        # Control request with no data stage (Host-to-device)
        try:
            request_type = 0x40                         # Host-to-device, Vendor request to Device
            request = 0x20                              # Nonsense request
            value = 0                                   # Always 0 for this request
            index = 0                                   # Communication interface
            length = 0
            dev.ctrl_transfer(request_type, request, value, index, length, 5000)
            log("Invalid request not stalled")
        except usb.core.USBError:
            log("Invalid request stalled")

        # Control IN stall
        try:
            request_type = 0xC0                         # Device-to-host, Vendor request to Device
            request = 0x20                              # Nonsense request
            value = 0                                   # Always 0 for this request
            index = 0                                   # Communication interface
            length = 255
            dev.ctrl_transfer(request_type, request, value, index, length, 5000)
            log("Invalid request not stalled")
        except usb.core.USBError:
            log("Invalid request stalled")

        for i in (6, 7, 5):
            try:
                request_type = 0x80
                request = 0x6                       # GET_DESCRIPTOR
                value = (0x03 << 8) | (i << 0)      # String descriptor index
                index = 0                           # Communication interface
                length = 255
                resp = dev.ctrl_transfer(request_type, request, value, index, length, 5000)
                log("Requesting string %s passed" % i)
            except usb.core.USBError:
                log("Requesting string %s failed" % i)
        return True
        #print("Received key %s = %s" % (key, value))
        #self.send_kv("base_time", 0)


def main():
    parser = ArgumentParser(description="USB basic test")
    parser.add_argument('serial', help='USB serial number of DUT')
    args = parser.parse_args()
    ret = test_device(args.serial)
    print("Test %s" % "passed" if ret else "failed")


if __name__ == "__main__":
    main()
