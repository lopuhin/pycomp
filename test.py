#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import unittest

from compiler import *
from utils import make_executable, capture_output


class TestWhole(unittest.TestCase):

    def test_noop(self):
        program = [FnDef('main', [], [Return(IntConst(0))])]
        self.check_output('test_noop', program, '')
        self.check_pp(program, '''
def main():
    return 0
        ''')

    def test_hello_world(self):
        program = [FnDef('main', [], [
                    FnCall('printf', [StringConst('Hello, World!\n')]),
                    FnCall('puts', [StringConst('Bye!')]),
                    Return(IntConst(0))]
                )]
        self.check_output('test_hello_world', program, 
                'Hello, World!\nBye!\n')
        self.check_pp(program, '''
def main():
    printf("Hello, World!\\n")
    puts("Bye!")
    return 0
        ''')

    def test_multi_args(self):
        args = map(str, xrange(1, 12))
        program = [
            FnDef('main', [], [
                FnCall('printf', [
                    StringConst('Hello, %d-st user %s!\n'),
                    IntConst(1),
                    StringConst('kostia')]),
                FnCall('printf', 
                    map(StringConst, [' '.join('%s' * len(args))] + args)),
                Return(IntConst(0))]
                )]
        self.check_output('test_multi_args', program, 
                'Hello, 1-st user kostia!\n' + ' '.join(args))

    def check_output(self, test_name, program, expected):
        asm_output = compile_program(program)
        test_executable = make_executable(test_name, asm_output)
        output = capture_output(test_executable)
        self.assertEqual(expected, output)
    
    def check_pp(self, program, expected):
        pp = pp_join('\n', program)
        self.assertEqual(pp.strip(' \n'), expected.strip(' \n'))


if __name__ == '__main__':
    unittest.main()


