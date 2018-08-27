#!/usr/bin/env python

import argparse

from duel.assembler import assemble


def asm_func(args):
    assemble(args.inp, args.outp)


parser = argparse.ArgumentParser(
    prog='duel',
    add_help=True,
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    default=False,
    help='turn on debug msg'
)

parser.set_defaults(func=lambda x: parser.print_help())

subparsers = parser.add_subparsers(help='duel commands')

asm_parser = subparsers.add_parser(
    'asm',
    help='assemble input file to machine code',
)

asm_parser.add_argument(
    '-i', '--inp',
    required=True,
    help='input asm file path',
)

asm_parser.add_argument(
    '-o', '--outp',
    required=True,
    help='output machine code file path',
)

asm_parser.set_defaults(func=asm_func)


def main():
    args = parser.parse_args()
    return args.func(args)
