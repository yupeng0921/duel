#!/usr/bin/env python

from duel.instructions import InsDump, InsInfo, DumpError, \
    reg_name_to_idx, reg_idx_to_name, InsRun, InsError


class AddDump(InsDump):
    '''
    add %r1, %r0 // add r1 and r0, store result to r0
    add $42, %r0 // add 42 and r0, store result to r0
    add $a_label, %r0 // add the address of a_label and r0, store result to r0
    '''

    op_code = 0x05

    @classmethod
    def get_name(self):
        return 'add'

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


class AddRun(InsRun):

    @classmethod
    def get_op_code(self):
        return 0x05

    def run_ins(self, ins_info, reg_dict, ctx):
        if ins_info.option == 0x1:
            reg_a = reg_idx_to_name.get(ins_info.reg_a)
            if reg_a is None:
                raise InsError('invalid reg_a: 0x%x' % ins_info.reg_a)
            reg_b = reg_idx_to_name.get(ins_info.get_b)
            if reg_b is None:
                raise InsError('inserror reg_b: 0x%x' % ins_info.reg_b)
            # FIXME handle sign and flags
            val = reg_dict[reg_b]
            reg_dict[reg_a] += val
        elif ins_info.option == 0x2:
            reg_a = reg_idx_to_name.get(ins_info.reg_a)
            if reg_a is None:
                raise InsError('invalid reg_a: 0x%x' % ins_info.reg_a)
            val = ins_info.immediate & 0x7fff
            sign = ins_info.immediate & 0x8000
            # FIXME handle sign and flags
            assert(sign == 0)
            reg_dict[reg_a] += val
        else:
            raise InsError('invalid option: 0x%x' % ins_info.option)
