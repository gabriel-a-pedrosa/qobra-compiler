# A compiler for Qobra

Qobra is a small imperative programming language that we designed for this
project, and this is its compiler. We defined the language's syntax and
grammar, and built a lexer, an LALR parser, a symbol table and a code generator
that emits stack assembly for the [EWVM](https://ewvm.epl.di.uminho.pt/)
virtual machine. It is written in Python with PLY.

## The language

```c
int n;
int result;
int aux;

function factorial() {
    aux = 1;
    repeat
        aux = aux * n;
        n = n - 1;
    until n == 0
    return aux
}

read(n);
result = factorial();
write(result);

if result > 100 then
    write(1);
else
    write(0);
end
```

Qobra has integer variables, `read` and `write`, `if`/`elif`/`else`,
`repeat`/`until` loops, parameterless functions and the usual arithmetic,
comparison and Boolean operators (`or` binds loosest, then `and`, `not`,
comparisons, `+ -` and `* /`).

## Usage

```bash
pip install -r requirements.txt
python -m qobra examples/factorial.qbr
```

This prints the EWVM assembly, which runs directly in the
[EWVM web interface](https://ewvm.epl.di.uminho.pt/). Use `-o file.vm` to save
it to a file. Errors exit with status 1, and lexer and parser errors also
report the line.

```python
from qobra import compile_source
code = compile_source("int x; x = 1 + 2; write(x);")
```

## How it works

1. **Lexing and parsing.** PLY turns the source into an abstract syntax tree of
   tuples such as `("assign", name, expr)`.
2. **Symbol table.** Every variable is global and gets an offset in declaration
   order, read and written with `PUSHG` and `STOREG`.
3. **Code generation.** Expressions compile to postfix, which is exactly what a
   stack machine expects. Loops and conditionals use numbered labels with `JZ`
   and `JUMP`, and functions are emitted after the main program and called with
   `PUSHA` and `CALL`.

## Repository layout

```
qobra/          lexer.py, parser.py, codegen.py, cli.py
examples/       sample programs, plus one failing program per kind of error
tests/          checks on the generated code and on the errors
docs/           the course report
```

## Credits

Group project for Language Theory and Compilation (MSc in Engineering
Physics, University of Minho, 2024/25), by Gabriel A. Pedrosa and Pedro
Magalhães.
