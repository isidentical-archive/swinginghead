from lark import Lark
from lark.indenter import Indenter


def get_parser():
    return Lark.open("GRAMMAR", parser="earley", rel_to=__file__)
