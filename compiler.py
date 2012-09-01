#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from operator import itemgetter

from utils import compile_nodes, reindent


def compile_program(body):
    env = Environment()
    preambule = '''
        .file        "test.c"
        .section     .rodata
    '''
    program = compile_nodes(body, env)
    output = preambule + env.get_const_section() + program
    output += '''
    .LFE0:
        .size    main, .-main
    '''
    return reindent(output)


class Environment(object):
    def __init__(self):
        self.const_labels = {}
        self.fn_labels = {}

    def get_const_label(self, value):
        if value in self.const_labels:
            return self.const_labels[value]
        else:
            label = self.const_labels[value] = '.LC%d' % len(self.const_labels)
            return label

    def get_fn_label(self, name):
        if name in self.fn_labels:
            return self.fn_labels[name]
        else:
            label = self.fn_labels[name] = '.LFB%d' % len(self.fn_labels)
            return label

    def get_const_section(self):
        output = ''
        for value, label in sorted(self.const_labels.iteritems(), 
                key=itemgetter(1)):
            output += '''
            {label}:
                .string "{value}"
            '''.format(label=label, value=value.encode('string_escape'))
            # FIXME - " quotes
        return output 


class AstNode(object):
    def compile(self, env):
        raise NotImplementedError


class FnDef(AstNode):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def compile(self, env):
        fn_label = env.get_fn_label(self.name)
        output = '''
            .text
            .globl   {name}
            .type    {name}, @function
        {name}:
        {fn_label}:
            .cfi_startproc
            pushq    %rbp
            .cfi_def_cfa_offset 16
            .cfi_offset 6, -16
            movq     %rsp, %rbp
            .cfi_def_cfa_register 6
        '''.format(name=self.name, fn_label=fn_label)
        output += compile_nodes(self.body, env)
        output += '''
            popq    %rbp
            .cfi_def_cfa 7, 8
            ret
            .cfi_endproc
        '''
        return output


class FnCall(AstNode):
    def __init__(self, fn_name, args):
        self.fn_name = fn_name
        self.args = args

    def compile(self, env):
        assert len(self.args) == 1
        return '''
            movl    {arg}, %edi
            call    {fn_name}
        '''.format(
                arg=self.args[0].compile(env),
                fn_name=self.fn_name)


class Return(AstNode):
    def __init__(self, value):
        self.value = value

    def compile(self, env):
        return '''
            movl    {value}, %eax
        '''.format(value=self.value.compile(env))


class ValueNode(AstNode):
    def __init__(self, value):
        self.value = value


class StringConst(ValueNode):
    def compile(self, env):
        const_label = env.get_const_label(self.value)
        return '$%s' % const_label


class IntConst(ValueNode):
    def compile(self, env):
        return '$%d' % self.value


if __name__ == '__main__':
    print Compiler().compile(
            [["puts", "Foo, bar"],
             ["printf", "Hello World!\\n"]]
            )


