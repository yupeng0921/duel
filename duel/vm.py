#!/usr/bin/env python

import random
from collections import namedtuple
import threading
import time
import struct
import curses
import logging

from duel.instructions import cc, ins_decode, Context, InsError
from duel.instructions.ins_mov import MovRun
from duel.instructions.ins_add import AddRun
from duel.instructions.ins_cmp import CmpRun
from duel.instructions.ins_str import StrRun
from duel.instructions.ins_jump import JcRun


logger = logging.getLogger('duel.vm')

ins_dict = {}
ins_dict[MovRun.get_op_code()] = MovRun
ins_dict[AddRun.get_op_code()] = AddRun
ins_dict[CmpRun.get_op_code()] = CmpRun
ins_dict[StrRun.get_op_code()] = StrRun
ins_dict[JcRun.get_op_code()] = JcRun


ProgInfo = namedtuple('ProgInfo', [
    'machine_code', 'init_addr'])


class VmThread(threading.Thread):

    def __init__(
            self, prog_info, mem, display_list, cpu_id, frequence,
            *args, **kwargs):
        self.prog_info = prog_info
        self.mem = mem
        self.running = True
        self.display_list = display_list
        self.reason = None
        self.cpu_id = str(cpu_id)
        self.frequence = frequence
        self.reg_dict = {
            'r0': 0,
            'r1': 0,
            'r2': 0,
            'r3': 0,
            'r4': 0,
            'r5': 0,
            'r6': 0,
            'r7': 0,
            'pc': 0,
            'flags': 0,
            'evt': 0,
            'sp': 0,
        }
        super(VmThread, self).__init__(*args, **kwargs)

    def run(self):
        msize = len(self.mem)
        ratio = msize / len(self.display_list)
        ctx = Context(
            self.mem, msize, self.display_list, ratio, self.cpu_id)
        for i in range(len(self.prog_info.machine_code)):
            idx = self.prog_info.init_addr + i
            self.mem[idx] = self.prog_info.machine_code[i]
            idx1 = int(idx / ratio)
            self.display_list[idx1] = self.cpu_id
        self.reg_dict['pc'] = self.prog_info.init_addr
        interval = 1 / self.frequence
        prev_time = time.time()
        while self.running is True:
            curr_time = time.time()
            time_diff = curr_time - prev_time
            if time_diff < interval:
                time.sleep(interval-time_diff)
            prev_time = time.time()
            start = self.reg_dict['pc']
            stop = start + 4
            if stop > msize:
                if self.reg_dict['flags'] & cc.FLAG_EXC:
                    self.reason = 'double_fault'
                    return
                self.reg_dict['flags'] |= cc.FLAG_EXC
                self.reg_dict['pc'] = self.reg_dict['evt'] + cc.EXC_MEM_OOR
                continue
            ins = struct.unpack('<I', self.mem[start:stop])[0]
            ins_info = ins_decode(ins)
            self.reg_dict['pc'] += 4
            cls = ins_dict.get(ins_info.op_code)
            logger.debug(
                '%s: 0x%08x 0x%08x %s %s',
                self.cpu_id, self.reg_dict['pc'], ins, cls, ins_info)
            if cls is None:
                if self.reg_dict['flags'] & cc.FLAG_EXC:
                    self.reason = 'double_fault'
                    return
                self.reg_dict['flags'] |= cc.FLAG_EXC
                self.reg_dict['pc'] = self.reg_dict['evt'] + cc.EXC_INV_INS
                continue
            try:
                cls(ins_info, self.reg_dict, ctx).run()
            except InsError:
                if self.reg_dict['flags'] & cc.FLAG_EXC:
                    self.reason = 'double_fault'
                    return
                self.reg_dict['flags'] |= cc.FLAG_EXC
                self.reg_dict['pc'] = self.reg_dict['evt'] + cc.EXC_INV_INS
                continue

    def stop(self):
        self.running = False


class ScreenManager():

    def __init__(self):
        screen = curses.initscr()
        screen.clear()
        screen.border(0)
        lines = curses.LINES - 2
        cols = curses.COLS - 2
        self.screen = screen
        self.lines = lines
        self.cols = cols
        self.screen_size = lines * cols

    def update(self, display_list):
        offset = 0
        for line in range(1, self.lines+1):
            start = offset
            stop = offset + self.cols
            data = ''.join(display_list[start:stop])
            offset += self.cols
            self.screen.addstr(line, 1, data)
        self.screen.refresh()


def run_vm(inp_list, msize, csize, frequence):
    mem = bytearray(msize)
    mblock_set = set(range(msize//csize))
    prog_list = []
    for inp_info in inp_list:
        if ':' in inp_info:
            inp_path, init_addr_str = inp_info.split(':')
            with open(inp_path, 'rb') as f:
                machine_code = f.read()
            assert(len(machine_code) < csize)
            init_addr = int(init_addr_str)
            mblock_no = init_addr // csize
            if mblock_no not in mblock_set:
                raise Exception(
                    'init_addr invalid: %s' % init_addr_str)
            mblock_set.remove(mblock_no)
            real_init_addr = mblock_no * csize
            prog_info = ProgInfo(machine_code, real_init_addr)
            prog_list.append(prog_info)
        else:
            inp_path = inp_info
            with open(inp_path, 'rb') as f:
                machine_code = f.read()
            assert(len(machine_code) < csize)
            mblock_no = random.sample(mblock_set, 1)[0]
            mblock_set.remove(mblock_no)
            real_init_addr = mblock_no * csize
            prog_info = ProgInfo(machine_code, real_init_addr)
            prog_list.append(prog_info)

    sm = ScreenManager()
    display_list = ['.'] * sm.screen_size
    thread_list = []
    for cpu_id, prog_info in enumerate(prog_list):
        t = VmThread(prog_info, mem, display_list, cpu_id, frequence)
        t.start()
        thread_list.append(t)

    msg = None
    try:
        while True:
            sm.update(display_list)
            time.sleep(0.5)
            for t in thread_list:
                if t.reason is not None:
                    msg = 'cpu %s failed' % t.cpu_id
                    break
            if msg is not None:
                break
    except KeyboardInterrupt:
        for t in thread_list:
            t.stop()
            t.join()
    else:
        for t in thread_list:
            t.stop()
            t.join()
    finally:
        curses.endwin()

    i = 0
    while i < len(mem):
        items = []
        curr = i
        for j in range(8):
            items.append('0x%02x' % mem[i])
            i += 1
        line = ' '.join(items)
        logger.debug('%s %s', curr, line)
    print(msg)
