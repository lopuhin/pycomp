# -*- encoding: utf-8 -*-

import os.path
import subprocess


def compile_nodes(nodes, env):
    return '\n'.join(node.compile(env) for node in nodes)


def reindent(asm_output):
    indented = []
    for line in asm_output.split('\n'):
        line = line.strip()
        if line:
            if not line.endswith(':'):
                line = '    ' + line
            indented.append(line)
    return '\n'.join(indented) + '\n'


def shift_right(text, prefix='    '):
    return '\n'.join((prefix + l if l else '') for l in text.split('\n'))


def pp_join(sep, ast_nodes):
    return sep.join(node.pretty_print() for node in ast_nodes)


def make_executable(name, asm_output):
    source_name = os.path.join('.', name + '.s')
    output_name = os.path.join('.', name + '.out')
    with open(source_name, 'w') as f:
        f.write(asm_output)
    subprocess.check_call(['gcc', '-o', output_name, source_name])
    return output_name


def capture_output(name):
    return subprocess.check_output(name)

        

