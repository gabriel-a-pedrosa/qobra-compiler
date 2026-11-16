"""Qobra compiler: Qobra source code -> EWVM assembly."""

import sys

from .lexer import lexer
from .parser import parser, reset_lexer_line
from . import codegen

__all__ = ["compile_source"]


def compile_source(text):
    """Compile Qobra source text into a list of EWVM instructions."""
    codegen._label_counter = 0

    # 1) LEXING
    try:
        lexer.input(text)
        for _ in lexer:
            pass
    except Exception:
        sys.exit(1)

    # 2) PARSING
    try:
        reset_lexer_line(lexer)
        ast = parser.parse(text)
    except Exception:
        sys.exit(1)

    # 3) COMPILING
    return codegen.generate_code(ast)
