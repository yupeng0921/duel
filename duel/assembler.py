#!/usr/bin/env python

from collections import namedtuple
import re

from duel.utils import AssembleError
from duel.instructions import DumpError
from duel.instructions.mov import MovDump


Instruction = namedtuple('Instruction', [
    'name', 'line_no', 'params'])


label_pattern = re.compile('[a-z,A-Z,_][a-z,A-Z,0-9,_]*')


ins_dict = {}
ins_dict[MovDump.get_name()] = MovDump


def assemble(inp_path, outp_path):
    with open(inp_path) as inp_f:
        with open(outp_path, 'wb') as outp_f:
            ins_list = []
            label_dict = {}
            pos = 0
            line_no = 0
            for eachline in inp_f:
                line_no += 1
                idx = eachline.find('//')
                if idx >= 0:
                    eachline = eachline[:idx]
                eachline = eachline.strip().lower()
                if eachline == '':
                    continue
                elif eachline.endswith(':'):
                    label = eachline[:-1]
                    if not label_pattern.match(label):
                        reason = 'invalid label: %s' % label
                        raise AssembleError(line_no, reason)
                    label_dict[label] = pos
                else:
                    idx = eachline.find(' ')
                    params = []
                    if idx == -1:
                        name = eachline
                    else:
                        name = eachline[:idx]
                        for item in eachline[idx:].split(','):
                            params.append(item.strip())
                    ins = Instruction(name, line_no, params)
                    ins_list.append(ins)
                    pos += 4
            for ins in ins_list:
                cls = ins_dict.get(ins.name)
                if cls is None:
                    reason = 'unkonwn ins name: %s' % ins.name
                    raise AssembleError(ins.line_no, reason)
                try:
                    machine_code = cls(ins.params, label_dict).dump()
                except DumpError as e:
                    raise AssembleError(ins.line_no, str(e))
                outp_f.write(machine_code)
