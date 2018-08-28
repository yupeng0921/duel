#!/usr/bin/env python

import argparse
import logging

from duel.assembler import assemble
from duel.vm import run_vm


def asm_func(args):
    assemble(args.inp, args.outp)


def run_func(args):
    run_vm(args.inp, args.msize, args.csize, args.frequence)


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


run_parser = subparsers.add_parser(
    'run',
    help='run machine code in vm',
)

run_parser.add_argument(
    '-i', '--inp',
    action='append',
    required=True,
    help='machine code file, and optional load address',
)

run_parser.add_argument(
    '-m', '--msize',
    default=8192,
    help='vm memory size',
)

run_parser.add_argument(
    '-c', '--csize',
    default=512,
    help='max machine code size',
)

run_parser.add_argument(
    '-f', '--frequence',
    default=100,
    type=int,
    help='frequence of the vm',
)

run_parser.set_defaults(func=run_func)


def main():
    args = parser.parse_args()
    if args.debug is True:
        logging.basicConfig(filename='duel.log', level=logging.DEBUG)
    return args.func(args)
