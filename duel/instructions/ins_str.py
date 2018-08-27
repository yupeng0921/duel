#!/usr/bin/env python

from duel.instructions import InsDump, InsInfo, DumpError, \
    reg_name_to_idx, reg_idx_to_name, InsRun, InsError


class StrDump(InsDump):
    '''
    str %r1, %r0 // store the value of r1 to the address in r0
    str $42, %r0 // store 42 to the address in r0
    str $a_label, %r0 // store address of a_label to the address in r0
    '''

    op_code = 0x04

    @classmethod
    def get_name(self):
        return 'str'

    def get_ins_info(self, params, label_dict):
        if params[0].startswith('%'):
            return self.op_01(params, label_dict)
        elif params[0].startswith('$'):
            return self.op_10(params, label_dict)
        else:
            raise DumpError('unknonw param0 type')

    def op_01(self, params, label_dict):
        reg_b_name = params[0][1:]
        reg_b_idx = reg_name_to_idx.get(reg_b_name)
        if reg_b_idx is None:
            raise DumpError('reg_b name wrong: %s' % reg_b_name)
        if not params[1].startswith('%'):
            raise DumpError('reg_a is not start with %')
        reg_a_name = params[1][1:]
        reg_a_idx = reg_name_to_idx.get(reg_a_name)
        if reg_a_idx is None:
            raise DumpError('reg_a name wrong: %s' % reg_a_name)
        option = 0x1
        immediate = 0
        return InsInfo(self.op_code, option, reg_a_idx, reg_b_idx, immediate)

    def op_10(self, params, label_dict):
        immediate_str = params[0][1:]
        immediate = label_dict.get(immediate_str)
        if immediate is None:
            try:
                immediate = int(immediate_str)
            except ValueError:
                raise DumpError('invalid immediate: %s' % immediate_str)
        reg_a_name = params[1][1:]
        reg_a_idx = reg_name_to_idx.get(reg_a_name)
        if reg_a_idx is None:
            raise DumpError('reg_a name wrong: %s' % reg_a_name)
        option = 0x2
        reg_b_idx = 0
        return InsInfo(self.op_code, option, reg_a_idx, reg_b_idx, immediate)


class StrRun(InsRun):

    @classmethod
    def get_op_code(self):
        return 0x04

    def run_ins(self, ins_info, reg_dict, ctx):
        if ins_info.option == 0x1:
            reg_a = reg_idx_to_name.get(ins_info.reg_a)
            if reg_a is None:
                raise InsError('invalid reg_a: 0x%x' % ins_info.reg_a)
            reg_b = reg_idx_to_name.get(ins_info.get_b)
            if reg_b is None:
                raise InsError('inserror reg_b: 0x%x' % ins_info.reg_b)
            val = reg_dict[reg_b]
            addr = reg_dict[reg_a]
            if (addr & 0x80000000):
                raise InsError('negative addr: 0x%x' % addr)
            if addr >= ctx.msize:
                raise InsError('addr out of range: 0x%x' % addr)
            ctx.mem[addr] = val
        elif ins_info.option == 0x2:
            reg_a = reg_idx_to_name.get(ins_info.reg_a)
            if reg_a is None:
                raise InsError('invalid reg_a: 0x%x' % ins_info.reg_a)
            addr = reg_dict[reg_a]
            val = ins_info.immediate
            sign = ins_info.immediate & 0x8000
            if (addr & 0x80000000):
                raise InsError('negative addr: 0x%x' % addr)
            if addr >= ctx.msize:
                raise InsError('addr out of range: 0x%x' % addr)
            ctx.mem[addr] = val
            if sign:
                ctx.mem[addr] |= 0x80000000
        else:
            raise InsError('invalid option: 0x%x' % ins_info.option)
