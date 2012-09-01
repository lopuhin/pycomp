#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from operator import itemgetter

from utils import compile_nodes, reindent, shift_right, pp_join


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

    def pretty_print(self):
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
    
    def pretty_print(self):
        heading = 'def {name}({args}):'.format(
                name=self.name, args=pp_join(', ', self.args))
        return heading + '\n' + shift_right(pp_join('\n', self.body))


class FnDefArg(AstNode):
    def __init__(self, name):
        self.name = name

    def pretty_print(self):
        return self.name


class FnCall(AstNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def compile(self, env):
        assert len(self.args) == 1
        return '''
            movl    {arg}, %edi
            call    {name}
        '''.format(
                arg=self.args[0].compile(env),
                name=self.name)

    def pretty_print(self):
        return '{name}({args})'.format(
                name=self.name, args=pp_join(', ', self.args))


class Return(AstNode):
    def __init__(self, value):
        self.value = value

    def compile(self, env):
        return '''
            movl    {value}, %eax
        '''.format(value=self.value.compile(env))

    def pretty_print(self):
        return 'return {value}'.format(value=self.value.pretty_print())


class ValueNode(AstNode):
    def __init__(self, value):
        self.value = value

    def pretty_print(self):
        return unicode(self.value)


class StringConst(ValueNode):
    def compile(self, env):
        const_label = env.get_const_label(self.value)
        return '$%s' % const_label
    
    def pretty_print(self):
        # FIXME - " quotes
        return '"%s"' % self.value.encode('string_escape') 


class IntConst(ValueNode):
    def compile(self, env):
        return '$%d' % self.value
