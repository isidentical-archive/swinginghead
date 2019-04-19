from ast import literal_eval
from contextlib import nullcontext
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any, Callable, Optional, Sequence, Union

import llvmlite.ir as ir
from lark import Token, Transformer

from swinginghead.parser.pgen import get_parser


@dataclass
class Name:
    arg: Union[str, int]
    nam: bool = False


@dataclass
class Operation:
    ope: str
    args: Sequence


@dataclass
class Comparison:
    ope: str
    args: Sequence


@dataclass
class Equality:
    name: Name
    value: Any


@dataclass
class Return:
    value: Any


class Custom:
    def register(self, instr):
        self.content.append(instr)


@dataclass
class IfDecl(Custom):
    comp: Comparison
    content: Sequence
    elsecontent: Sequence


OP_MAP = {"+": "add", "-": "sub", "*": "mul", "/": "div"}
CMP_MAP = {"gt": ">", "lt": "<", "ge": ">=", "le": "<=", "eq": "==", "ne": "!="}


class Compiler(Transformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module = ir.Module(name="<swinginghead>")
        self._reg_map = {}
        self._fun_types = {}
        self._last_fun_ann = None

    def start(self, tokens):
        return tokens

    def pointer(self, tokens):
        return ir.PointerType(tokens.pop())

    def literal(self, tokens):
        vmtype, value = tokens
        if isinstance(vmtype, (ir.VectorType, ir.Aggregate)):
            return vmtype([literal_eval(token.value) for token in value.children])
        elif isinstance(vmtype, ir.VoidType):
            return vmtype

        return vmtype(literal_eval(value))

    def typedecl(self, tokens):
        vmtype = tokens.pop(0)
        vmtype = getattr(ir, f"{vmtype.capitalize()}Type")
        try:
            if issubclass(vmtype, (ir.VectorType, ir.Aggregate)):
                element, count = [tree.children.pop() for tree in tokens]
                vmtype = vmtype(element, literal_eval(count))
            else:
                vmtype = vmtype(literal_eval(tokens.pop().children.pop()))
        except IndexError:
            vmtype = vmtype()

        return vmtype

    def functypedecl(self, tokens):
        return ir.FunctionType(tokens.pop(0), tokens)

    def funcdecl(self, tokens):
        vmtype, name, *statements = tokens
        self._fun_types[name] = vmtype
        name = str(name)
        func = ir.Function(self.module, vmtype, name=name)
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)
        for statement in statements:
            self.dispatch(func, builder, statement)

        return func

    def ifdecl(self, tokens):
        comp = tokens.pop(0)
        ifsuite = tokens.pop(0).children
        elsesuite = [] if len(tokens) < 1 else tokens.pop(0).children
        return IfDecl(comp, ifsuite, elsesuite)

    def operation(self, tokens):
        lhs, op, rhs = tokens
        if len(op) > 1:
            op = f"{op[0]}{OP_MAP[op[1]]}"
        else:
            op = OP_MAP[op]

        return Operation(op, (lhs, rhs))

    def comparison(self, tokens):
        lhs, comp, rhs = tokens
        comp = comp.split(" ")
        op = f"{comp.pop(0)}cmp_{comp.pop(0)}"
        return Comparison(op, [*comp, lhs, rhs])

    def equality(self, tokens):
        name, value = tokens
        name = Name(name)
        return Equality(name, value)

    def returns(self, tokens):
        return Return(tokens.pop())

    def local_name(self, tokens):
        name = tokens.pop()
        if name.isdigit():
            return Name(int(name) - 1)
        else:
            return Name(name, True)

    def compile(self, tree):
        self.transform(tree)
        return self.module

    def ifdecl_builder(self, func, builder, statement):
        pred = self.dispatch(func, builder, statement.comp)
        with builder.if_else(pred) as (then, otherwise):
            with then:
                for stmt in statement.content:
                    self.dispatch(func, builder, stmt)

            with otherwise:
                for stmt in statement.elsecontent:
                    self.dispatch(func, builder, stmt)

    def operation_builder(self, func, builder, statement):
        return getattr(builder, statement.ope)(*self.arg_parser(func, statement.args))

    def comparison_builder(self, func, builder, statement):
        return getattr(builder, statement.ope)(
            CMP_MAP[statement.args.pop(0)], *self.arg_parser(func, statement.args)
        )

    def equality_builder(self, func, builder, statement):
        val = self.dispatch(func, builder, statement.value)
        val.name = statement.name.arg
        self._reg_map[val.name] = val
        return val

    def return_builder(self, func, builder, statement):
        builder.ret(*self.arg_parser(func, (statement.value,)))

    def dispatch(self, func, builder, statement):
        return getattr(self, f"{statement.__class__.__name__.lower()}_builder")(
            func, builder, statement
        )

    def arg_parser(self, func, args):
        new_args = []
        for arg in args:
            if isinstance(arg, Name):
                if arg.nam:
                    arg = self._reg_map[arg.arg]
                else:
                    arg = func.args[arg.arg]

            new_args.append(arg)
        return new_args
