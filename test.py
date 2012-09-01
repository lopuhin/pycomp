#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import unittest

from compiler import *
from utils import make_executable, capture_output


class TestWhole(unittest.TestCase):

    def test_noop(self):
        output = compile_program(
                [FnDef('main', [], [Return(IntConst(0))])]
                ) 
        self.check_output('test_noop', output, '')

    def test_hello_world(self):
        output = compile_program(
                [FnDef('main', [], [
                    FnCall('printf', [StringConst('Hello, World!\n')]),
                    Return(IntConst(0))]
                )])
        self.check_output('test_hello_world', output, 'Hello, World!\n')

    def check_output(self, test_name, asm_output, expected):
        test_executable = make_executable(test_name, asm_output)
        output = capture_output(test_executable)
        self.assertEqual(expected, output)


if __name__ == '__main__':
    unittest.main()


