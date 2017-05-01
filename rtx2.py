"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2016 ARM Limited

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
from pyOCD.board import MbedBoard
from pyOCD.rtos.provider import (TargetThread, ThreadProvider)
from pyOCD.rtos.common import (read_c_string, HandlerModeThread)
from pyOCD.debug.context import DebugContext
import logging
from collections import namedtuple

RTX2_osRtxInfo_t = {
    "kernel.state": 8,
    "run.curr": 28,
    "ready.thread_list": 44,
    "delay_list": 52,
    "wait_list": 56
}

RTX2_osRtxThread_t = {
    "name": 4,
    "thread_next": 8,
    "thread_prev": 12,
    "delay_next": 16,
    "delay_prev": 20,
    "stack_mem": 48,
    "stack_size": 52,
    "sp": 56,
    "thread_addr": 60,
}

RTX2_osKernelState_t = {
    "osKernelInactive": 0,
    "osKernelReady": 1,
    "osKernelRunning": 2,
    "osKernelLocked": 3,
    "osKernelSuspended": 4,
    "osKernelError": 0xFFFFFFFF,
}

log = logging.getLogger("rtx2")


class FreeRTOSThreadContext(DebugContext):
    # SP/PSP are handled specially, so it is not in these dicts.

    COMMON_REGISTER_OFFSETS = {
                 4: 0, # r4
                 5: 4, # r5
                 6: 8, # r6
                 7: 12, # r7
                 8: 16, # r8
                 9: 20, # r9
                 10: 24, # r10
                 11: 28, # r11
            }

    NOFPU_REGISTER_OFFSETS = {
                 0: 32, # r0
                 1: 36, # r1
                 2: 40, # r2
                 3: 44, # r3
                 12: 48, # r12
                 14: 52, # lr
                 15: 56, # pc
                 16: 60, # xpsr
            }
    NOFPU_REGISTER_OFFSETS.update(COMMON_REGISTER_OFFSETS)

    FPU_BASIC_REGISTER_OFFSETS = {
                -1: 32, # exception LR
                 0: 36, # r0
                 1: 40, # r1
                 2: 44, # r2
                 3: 48, # r3
                 12: 42, # r12
                 14: 56, # lr
                 15: 60, # pc
                 16: 64, # xpsr
            }
    FPU_BASIC_REGISTER_OFFSETS.update(COMMON_REGISTER_OFFSETS)

    FPU_EXTENDED_REGISTER_OFFSETS = {
                -1: 32, # exception LR
                 0x50: 36, # s16
                 0x51: 40, # s17
                 0x52: 44, # s18
                 0x53: 48, # s19
                 0x54: 52, # s20
                 0x55: 56, # s21
                 0x56: 60, # s22
                 0x57: 64, # s23
                 0x58: 68, # s24
                 0x59: 72, # s25
                 0x5a: 76, # s26
                 0x5b: 80, # s27
                 0x5c: 84, # s28
                 0x5d: 88, # s29
                 0x5e: 92, # s30
                 0x5f: 96, # s31
                 0: 100, # r0
                 1: 104, # r1
                 2: 108, # r2
                 3: 112, # r3
                 12: 116, # r12
                 14: 120, # lr
                 15: 124, # pc
                 16: 128, # xpsr
                 0x40: 132, # s0
                 0x41: 136, # s1
                 0x42: 140, # s2
                 0x43: 144, # s3
                 0x44: 148, # s4
                 0x45: 152, # s5
                 0x46: 156, # s6
                 0x47: 160, # s7
                 0x48: 164, # s8
                 0x49: 168, # s9
                 0x4a: 172, # s10
                 0x4b: 176, # s11
                 0x4c: 180, # s12
                 0x4d: 184, # s13
                 0x4e: 188, # s14
                 0x4f: 192, # s15
                 33: 196, # fpscr
                 # (reserved word: 200)
            }
    FPU_EXTENDED_REGISTER_OFFSETS.update(COMMON_REGISTER_OFFSETS)

    # Registers that are not available on the stack for exceptions.
    EXCEPTION_UNAVAILABLE_REGS = (4, 5, 6, 7, 8, 9, 10, 11)

    def __init__(self, parentContext, thread):
        super(FreeRTOSThreadContext, self).__init__(parentContext.core)
        self._parent = parentContext
        self._thread = thread
        self._has_fpu = parentContext.core.has_fpu

    def readCoreRegistersRaw(self, reg_list):
        reg_list = [self.registerNameToIndex(reg) for reg in reg_list]
        reg_vals = []

        inException = self._get_ipsr() > 0
        isCurrent = self._thread.is_current

        # If this is the current thread and we're not in an exception, just read the live registers.
        if isCurrent and not inException:
            return self._parent.readCoreRegistersRaw(reg_list)

        sp = self._thread.get_stack_pointer()

        # Determine which register offset table to use and the offsets past the saved state.
        realSpOffset = 0x40
        realSpExceptionOffset = 0x20
        table = self.NOFPU_REGISTER_OFFSETS
        if self._has_fpu:
            try:
                # Read stacked exception return LR.
                offset = self.FPU_BASIC_REGISTER_OFFSETS[-1]
                exceptionLR = self._parent.read32(sp + offset)

                # Check bit 4 of the saved exception LR to determine if FPU registers were stacked.
                if (exceptionLR & (1 << 4)) != 0:
                    table = self.FPU_BASIC_REGISTER_OFFSETS
                    realSpOffset = 0x44
                else:
                    table = self.FPU_EXTENDED_REGISTER_OFFSETS
                    realSpOffset = 0xcc
                    realSpExceptionOffset = 0x6c
            except DAPAccess.TransferError:
                log.debug("Transfer error while reading thread's saved LR")

        for reg in reg_list:
            # Check for regs we can't access.
            if isCurrent and inException:
                if reg in self.EXCEPTION_UNAVAILABLE_REGS:
                    reg_vals.append(0)
                    continue
                if reg == 18 or reg == 13: # PSP
                    reg_vals.append(sp + realSpExceptionOffset)
                    continue

            # Must handle stack pointer specially.
            if reg == 13:
                reg_vals.append(sp + realSpOffset)
                continue

            # Look up offset for this register on the stack.
            spOffset = table.get(reg, None)
            if spOffset is None:
                reg_vals.append(self._parent.readCoreRegisterRaw(reg))
                continue
            if isCurrent and inException:
                spOffset -= realSpExceptionOffset #0x20

            try:
                reg_vals.append(self._parent.read32(sp + spOffset))
            except DAPAccess.TransferError:
                reg_vals.append(0)

        return reg_vals

    def _get_ipsr(self):
        return self._parent.readCoreRegister('xpsr') & 0xff

    def writeCoreRegistersRaw(self, reg_list, data_list):
        self._parent.writeCoreRegistersRaw(reg_list, data_list)

## @brief Base class representing a thread on the target.
class RTX2TargetThread(TargetThread):
    RUNNING = 1
    READY = 2
    DELAYED = 3
    WAITING = 4

    STATE_NAMES = {
        RUNNING : "Running",
        READY : "Ready",
        DELAYED : "Delayed",
        WAITING : "Waiting",
    }

    def __init__(self, targetContext, provider, base, state):
        super(RTX2TargetThread, self).__init__()
        self._target_context = targetContext
        self._provider = provider
        self._base = base
        #TODO - create a new context
        self._thread_context = targetContext
        self._state = state
        
        name_addr = self._target_context.read32(self._base +
                                                RTX2_osRtxThread_t["name"])
        self._name = read_c_string(self._target_context, name_addr)
        if len(self._name) == 0:
            self._name = "Unnamed"

#TODO
    def get_stack_pointer(self):
        if self.is_current:
            # Read live process stack.
            sp = self._target_context.readCoreRegister('psp')
        else:
            # Get stack pointer saved in thread struct.
            try:
                sp = self._target_context.read32(self._base + THREAD_STACK_POINTER_OFFSET)
            except DAPAccess.TransferError:
                log.debug("Transfer error while reading thread's stack pointer @ 0x%08x", self._base + THREAD_STACK_POINTER_OFFSET)
        return sp

    @property
    def unique_id(self):
        return self._base

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self.STATE_NAMES[self._state]

    @property
    def is_current(self):
        return self._provider.get_actual_current_thread_id() == self.unique_id

    @property
    def context(self):
        return self._thread_context

    def __str__(self):
        return "<RTX2Thread@0x%08x id=%x name=%s>" % (id(self), self.unique_id, self.name)

    def __repr__(self):
        return str(self)


class RTX2ThreadProvider(ThreadProvider):
    
    """Required RTX2 Symbols"""
    REQUIRED_SYMBOLS = [
        "osRtxInfo",
        ]

    def __init__(self, target):
        super(RTX2ThreadProvider, self).__init__(target)
        self._target_context = self._target.getTargetContext()
        self._threads = {}
        self._os_rtx_info = None
        #todo

    def init(self, symbolProvider):
        symbols = self._lookup_symbols(self.REQUIRED_SYMBOLS,
                                             symbolProvider)
        if symbols is None:
            return False
        self._os_rtx_info = symbols['osRtxInfo']
        return True

    def _build_thread_list(self):
        ThreadLinkedList = namedtuple("ThreadLinkedList",
                                      "state address next_offset")
        lists_info = (
            ThreadLinkedList(
                state=RTX2TargetThread.READY,
                address=self._os_rtx_info + RTX2_osRtxInfo_t["ready.thread_list"],
                next_offset=RTX2_osRtxThread_t["thread_next"]
            ),
            ThreadLinkedList(
                state=RTX2TargetThread.DELAYED,
                address=self._os_rtx_info + RTX2_osRtxInfo_t["delay_list"],
                next_offset=RTX2_osRtxThread_t["delay_next"]
            ),
            ThreadLinkedList(
                state=RTX2TargetThread.WAITING,
                address=self._os_rtx_info + RTX2_osRtxInfo_t["wait_list"],
                next_offset=RTX2_osRtxThread_t["delay_next"]
            ),
        )
        threads = {}
        for state, address, next_offset in lists_info:
            for base in _iter_linked_list(self._target_context,
                                          address, next_offset):
                if base in self._threads:
                    log.error("Thread base 0x%x in multiple lists", base)
                    break
                threads[base] = RTX2TargetThread(self._target_context,
                                                       self, base, state)
        cur_base = self._target_context.read32(self._os_rtx_info + 
                                               RTX2_osRtxInfo_t["run.curr"])
        threads[cur_base] = RTX2TargetThread(self._target_context,
                                             self, cur_base, state)
        self._threads = threads

    def get_threads(self):
        if not self.is_enabled:
            return []
        self.update_threads()
        return self._threads.values()

    def get_thread(self, threadId):
        if not self.is_enabled:
            return None
        self.update_threads()
        return self._threads.get(threadId, None)

    @property
    def is_enabled(self):
        """Return True if the rtos is active, false otherwise"""
        if self._os_rtx_info is None:
            return False
        state = self._target_context.read32(self._os_rtx_info + 
                                            RTX2_osRtxInfo_t["kernel.state"])
        if state == RTX2_osKernelState_t["osKernelInactive"]:
            return False
        return True

    @property
    def current_thread(self):
        if not self.is_enabled:
            return None
        self.update_threads()
        id = self.get_current_thread_id()
        try:
            return self._threads[id]
        except KeyError:
            return None

    def is_valid_thread_id(self, threadId):
        if not self.is_enabled:
            return False
        self.update_threads()
        return threadId in self._threads

    def get_current_thread_id(self):
        if not self.is_enabled:
            return None
        if self.get_ipsr() > 0:
            #TODO - not sure what thread ID should be used here
            return 2
        return self._get_actual_current_thread_id()

    def get_ipsr(self):
        return self._target_context.readCoreRegister('xpsr') & 0xff

    def _get_actual_current_thread_id(self):
        if not self.is_enabled:
            return None
        return self._target_context.read32(self._os_rtx_info + 
                                           RTX2_osRtxInfo_t["run.curr"])

def analyze_rtos(target, base_addr):
    lists_info = (
        ("ready", base_addr + RTX2_osRtxInfo_t["ready.thread_list"], RTX2_osRtxThread_t["thread_next"]),
        ("delay", base_addr + RTX2_osRtxInfo_t["delay_list"], RTX2_osRtxThread_t["delay_next"]),
        ("wait", base_addr + RTX2_osRtxInfo_t["wait_list"], RTX2_osRtxThread_t["delay_next"]),
    )
    RUNNING = 1
    READY = 2
    DELAYED = 3
    WAITING = 4
    
    thread_lists = {name: list(_walk_linked_list(target, start, offset)) for name, start, offset in lists_info}
    thread_lists["running"] = [target.readMemory(base_addr + RTX2_osRtxInfo_t["run.curr"])]
    
    
    
    for name, thread_list in thread_lists.items():
        print(name)
        for thread in thread_list:
            print_tcb(target, thread)
    #print("Thread list: %s" % lists["delay"])
    #ready_list = list(walk_linked_list(target, RTX2_osRtxInfo_t["ready.thread_list"], ))


def _iter_linked_list(target, list_addr, next_offset):
    node = target.readMemory(list_addr)
    while node != 0:
        yield node
        node = target.readMemory(node + next_offset)

def main():
    with MbedBoard.chooseBoard() as board:
        analyze_rtos(board.target)
        #analyze_rtos(board.target, 0x20000010)

def analyze_rtos(target):
    class MockSymbolProvider(object):
        
        def get_symbol_value(self, symbol):
            if symbol == "osRtxInfo":
                return 0x20000010
            else:
                return None

    provider = RTX2ThreadProvider(target)
    provider.init(MockSymbolProvider())
    threads = provider.get_threads()
    for thread in threads:
        print("Thread: %s" % thread)
        
if __name__ == "__main__":
    main()

