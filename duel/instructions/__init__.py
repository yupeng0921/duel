#!/usr/bin/env python

from collections import namedtuple
from abc import ABC, abstractmethod
import struct


RegInfo = namedtuple('RegInfo', ['name', 'idx'])

reg_list = [
    RegInfo('r0', 0x0),
    RegInfo('r1', 0x1),
    RegInfo('r2', 0x2),
    RegInfo('r3', 0x3),
    RegInfo('r4', 0x4),
    RegInfo('r5', 0x5),
    RegInfo('r6', 0x6),
    RegInfo('r7', 0x7),
    RegInfo('pc', 0x8),
    RegInfo('flags', 0x9),
    RegInfo('evt', 0xa),
    RegInfo('sp', 0xb),
]

reg_name_to_idx = {}
for reg in reg_list:
    reg_name_to_idx[reg.name] = reg.idx

reg_idx_to_name = {}
for reg in reg_list:
    reg_idx_to_name[reg.idx] = reg.name


InsInfo = namedtuple('InsInfo', [
    'op_code', 'option', 'reg_a', 'reg_b', 'immediate'])


class DumpError(Exception):
    pass


class InsDump(ABC):

    def __init__(self, params, label_dict):
        self.params = params
        self.label_dict = label_dict

    @classmethod
    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @abstractmethod
    def get_ins_info(self):
        raise NotImplementedError

    def dump(self):
        ins_info = self.get_ins_info(self.params, self.label_dict)
        assert(ins_info.op_code >= 0)
        assert(ins_info.op_code < 64)
        assert(ins_info.option >= 0)
        assert(ins_info.option < 4)
        assert(ins_info.reg_a >= 0)
        assert(ins_info.reg_a < 16)
        assert(ins_info.reg_b >= 0)
        assert(ins_info.reg_b < 16)
        assert(ins_info.immediate >= 0)
        assert(ins_info.immediate < 65536)
        value = (ins_info.op_code << 26) + \
                (ins_info.option << 24) + \
                (ins_info.reg_a << 20) + \
                (ins_info.reg_b << 16) + \
                (ins_info.immediate)
        machine_code = struct.pack('<I', value)
        return machine_code
