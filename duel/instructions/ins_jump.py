#!/usr/bin/env python

from duel.instructions import InsDump, InsInfo, DumpError, \
    reg_name_to_idx, reg_idx_to_name, InsRun, InsError


class JcDump(InsDump):
    '''
    jc %r0 // if cf is 1, jump to r0
    jc $44 // if cf is 1, jump to address 44
    jc $a_label // if cf is 1, jump to address of a_label
    '''

    op_code = 0x11

    @classmethod
    def get_name(self):
        return 'jc'

    def get_ins_info(self, params, label_dict):
        if params[0].startswith('%'):
            return self.op_01(params, label_dict)
        elif params[0].startswith('$'):
            return self.op_10(params, label_dict)
        else:
            raise DumpError('unknonw param0 type')

    def op_01(self, params, label_dict):
        reg_a_name = params[0][1:]
        reg_a_idx = reg_name_to_idx.get(reg_a_name)
        if reg_a_idx is None:
            raise DumpError('reg_a name wrong: %s' % reg_a_name)
        reg_b_idx = 0
        option = 0x1
        immediate = 0
        return InsInfo(self.op_code, option, reg_a_idx, reg_b_idx, immediate)

    def op_10(self, params, label_dict):
        immediate_str = params[0][1:]
        immediate = label_dict.get(immediate_str)
        if immediate is None:
            try:
                if immediate_str.startswith('0x'):
                    immediate = int(immediate_str, 16)
                else:
                    immediate = int(immediate_str)
            except ValueError:
                raise DumpError('invalid immediate: %s' % immediate_str)
        option = 0x2
        reg_a_idx = 0
        reg_b_idx = 0
        return InsInfo(self.op_code, option, reg_a_idx, reg_b_idx, immediate)


class JcRun(InsRun):

    @classmethod
    def get_op_code(self):
        return 0x11

    def run_ins(self, ins_info, reg_dict, ctx):
        if ins_info.option == 0x1:
            reg_a = reg_idx_to_name.get(ins_info.reg_a)
            if reg_a is None:
                raise InsError('invalid reg_a: 0x%x' % ins_info.reg_a)
            val = reg_dict[reg_a] & 0x7fffffff
            sign = reg_dict[reg_a] & 0x80000000
            if sign:
                raise InsError('negative addr: 0x%x' % reg_dict[reg_a])
            if val >= ctx.msize:
                raise InsError('addr out of range: 0x%x' % reg_dict[reg_a])
            reg_dict['pc'] = reg_dict[reg_a]
        elif ins_info.option == 0x2:
            val = (ins_info.immediate & 0x7fff)
            sign = ins_info.immediate & 0x8000
            if sign == 0:
                val -= 4
                reg_dict['pc'] += val
            else:
                val += 4
                reg_dict['pc'] -= val
        else:
            raise InsError('invalid option: 0x%x' % ins_info.option)


class JncDump(InsDump):
    '''
    jnc %r0 // if cf is 0, jump to r0
    jnc $44 // if cf is 0, jump to address 44
    jnc $a_label // if cf is 0, jump to address of a_label
    '''

    op_code = 0x12

    @classmethod
    def get_name(self):
        return 'jnc'

    def get_ins_info(self, params, label_dict):
        if params[0].startswith('%'):
            return self.op_01(params, label_dict)
        elif params[0].startswith('$'):
            return self.op_10(params, label_dict)
        else:
            raise DumpError('unknonw param0 type')

    def op_01(self, params, label_dict):
        reg_a_name = params[0][1:]
        reg_a_idx = reg_name_to_idx.get(reg_a_name)
        if reg_a_idx is None:
            raise DumpError('reg_a name wrong: %s' % reg_a_name)
        reg_b_idx = 0
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
        option = 0x2
        reg_a_idx = 0
        reg_b_idx = 0
        return InsInfo(self.op_code, option, reg_a_idx, reg_b_idx, immediate)
