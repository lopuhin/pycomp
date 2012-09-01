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
                    Return(IntConst(0))]
                )]
        self.check_output('test_hello_world', program, 'Hello, World!\n')
        self.check_pp(program, '''
def main():
    printf("Hello, World!\\n")
    return 0
        ''')

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


