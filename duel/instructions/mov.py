#!/usr/bin/env python

from duel.instructions import InsDump, InsInfo, DumpError, \
    reg_name_to_idx


class MovDump(InsDump):
    '''
    mov $12, %r0 # store 12 to reg r0
    mov $a_label, $r0 # store the address of a_label to r0
    mov %r1, %r0 # store the value in reg r1 to reg r0
    '''

    op_code = 0x02

    @classmethod
    def get_name(self):
        return 'mov'

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
