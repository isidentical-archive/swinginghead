import llvmlite.ir as ir
from ast import literal_eval
from lark import Transformer
from swinginghead.parser.pgen import get_parser
from swinginghead.parser.elm import elmer
from dataclasses import dataclass
from typing import Callable, Sequence, Optional, Union, Any


@dataclass
class Name:
    arg: Union[str, int]
    nam: bool = False


@dataclass
class Operation:
    ope: Callable
    args: Sequence


@dataclass
class Equality:
    name: Name
    value: Any


@dataclass
class Return:
    value: Any

@dataclass
class NewBlocker:
    name: str

OP_MAP = {"+": "add", "-": "sub", "*": "mul", "/": "div"}


class Compiler(Transformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module = ir.Module(name="<swinginghead>")
        self._reg_map = {}

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
        name = str(name)
        func = ir.Function(self.module, vmtype, name=name)
        block = func.append_basic_block(name="entry")
        for statement in statements:
            if isinstance(statement, NewBlocker):
                block = func.append_basic_block(name=statement.name)
                
            builder = ir.IRBuilder(block)
            if not isinstance(statement, type(None)): # control for non dispatchable
                self.dispatch(func, builder, statement)

        return func

    def operation(self, tokens):
        lhs, op, rhs = tokens
        if len(op) > 1:
            op = f"{op[0]}{OP_MAP[op[1]]}"
        else:
            op = OP_MAP[op]

        return Operation(op, (lhs, rhs))

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

    def operation_builder(self, func, builder, statement):
        return getattr(builder, statement.ope)(*self.arg_parser(func, statement.args))

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


if __name__ == "__main__":
    parser = get_parser()
    compiler = Compiler()
    tree = parser.parse(
    """
    swing `float` $`float`€`float`$
    head {
        ,1 f+ (`float`->3.35)
        res eqs ,1 f+ ,2
        ./ ,res
    }
    """
    )
    result = compiler.compile(tree)
    print(result)
