from pathlib import Path

import pytest

from qobra import compile_source

ROOT = Path(__file__).resolve().parent.parent
ERROR_FILES = sorted((ROOT / "examples" / "errors").glob("*.qbr"))


def test_factorial_compiles():
    code = compile_source((ROOT / "examples" / "factorial.qbr").read_text(encoding="utf-8"))
    assert code[0] == "START"
    # Function bodies are emitted after the main program's STOP.
    assert "STOP" in code
    assert code.index("STOP") < code.index("factorial: NOP")


def test_program_without_functions_ends_with_stop():
    code = compile_source("int x; x = 7; write(x);")
    assert code[0] == "START"
    assert code[-1] == "STOP"


def test_showcase_compiles():
    code = compile_source((ROOT / "examples" / "showcase.qbr").read_text(encoding="utf-8"))
    assert code[0] == "START"


def test_error_examples_exist():
    assert len(ERROR_FILES) >= 6


@pytest.mark.parametrize("path", ERROR_FILES, ids=lambda p: p.name)
def test_error_examples_fail(path):
    with pytest.raises(SystemExit) as exc:
        compile_source(path.read_text(encoding="utf-8"))
    assert exc.value.code == 1


def test_simple_arithmetic():
    code = compile_source("int x; x = 1+2; write(x);")
    assert code == [
        "START", "PUSHI 0", "STOREG 0",
        "PUSHI 1", "PUSHI 2", "ADD", "STOREG 0",
        "PUSHG 0", "WRITEI", "WRITELN",
        "STOP",
    ]


def test_redeclared_variable_message(capsys):
    with pytest.raises(SystemExit):
        compile_source("int x; int x;")
    assert "redeclared" in capsys.readouterr().out


def test_compile_is_repeatable():
    src = "int x; read(x); if x > 0 then write(1); else write(0); end"
    assert compile_source(src) == compile_source(src)


def test_comparisons_inside_and():
    code = compile_source("int x; read(x); if x > 0 and x < 5 then write(1); end")
    i = code.index("AND")
    assert code[i - 6:i] == ["PUSHG 0", "PUSHI 0", "SUP", "PUSHG 0", "PUSHI 5", "INF"]


def test_unexpected_end_of_input(capsys):
    with pytest.raises(SystemExit):
        compile_source("int x; if x then")
    assert "end of input" in capsys.readouterr().out
