# qobra/codegen.py

import sys
_label_counter = 0
def fresh_label():
    global _label_counter
    lab = f"L{_label_counter}"
    _label_counter += 1
    return lab

class SymbolTable:
    def __init__(self):
        self.global_offset = 0
        self.symbols = {}
        self.functions = set()

    def add_var(self, name):
        if name in self.symbols:
            print(f"[Compiler Error] Variable '{name}' redeclared. This is not allowed in Qobra code.") 
            sys.exit(1)
        info = {"offset": self.global_offset}
        self.symbols[name] = info
        self.global_offset += 1

    def lookup_var(self, name):
        if name not in self.symbols:
            print(f"[Compiler Error] Variable '{name}' used without being declared. This is not allowed in Qobra code.") 
            sys.exit(1)
        return self.symbols[name]
    
    def add_function(self, name):
        if name in self.functions:
            print(f"[Compiler Error] Function '{name}' redeclared. This is not allowed in Qobra code.")
            sys.exit(1)
        self.functions.add(name)
        
    def lookup_function(self, name):
        if name not in self.functions:
            print(f"[Compiler Error] Function '{name}' used without being declared. This is not allowed in Qobra code.")
            sys.exit(1)


def generate_code(ast):
    # Initialize the symbol table and generated code
    st = SymbolTable()
    main_code = ["START"]
    func_code = []

    # Process variable declarations
    for d in ast[1]:  # Declarations list from the AST
        varName = d[1]
        st.add_var(varName)
        var_offset = st.lookup_var(varName)
        offset = var_offset['offset']
        main_code.append("PUSHI 0")
        main_code.append(f"STOREG {offset}")

    # Process statements
    for s in ast[2]:  # Statements list from the AST
        if s[0] == "function_decl":
            func_code.extend(gen_function_decl(s, st))
        else:
            main_code.extend(gen_stmt(s, st))

    # Finalize main code
    main_code.append("STOP")
    return main_code + func_code

def gen_stmt_list(stmt_list, st):
    code = []
    for s in stmt_list:
        try:
            code.extend(gen_stmt(s, st))
        except Exception as e:
            print(f"[Compiler Error] {str(e)}.")
            sys.exit(1)
    return code

def gen_stmt(snode, st):
    tag = snode[0]
    if tag == "assign":
        return gen_assign(snode, st)
    elif tag == "read":
        return gen_read(snode[1], st)
    elif tag == "write":
        return gen_write(snode[1], st)
    elif tag == "if":
        return gen_if(snode, st)
    elif tag == "repeat-until":
        return gen_repeat(snode, st)
    elif tag == "function_decl":
        return gen_function_decl(snode, st)
   

def gen_assign(node, st):
    varName, exprNode = node[1], node[2]
    varInfo = st.lookup_var(varName)
    code = gen_expr(exprNode, st)
    offset = varInfo["offset"]
    code.append(f"STOREG {offset}")
    return code


def gen_read(varName, st):
    varInfo = st.lookup_var(varName)
    offset = varInfo["offset"]
    return [
        "READ",
        "ATOI",
        f"STOREG {offset}"
    ]

def gen_write(exprNode, st):
    code = gen_expr(exprNode, st)
    code.append("WRITEI")
    code.append("WRITELN")
    return code

def gen_if(node, st):
    condExpr, ifStmts, elifList, elsePart = node[1], node[2], node[3], node[4]
    label_end = fresh_label()
    label_next = fresh_label()

    code = gen_expr(condExpr, st)
    code.append(f"JZ {label_next}")
    code.extend(gen_stmt_list(ifStmts, st))
    code.append(f"JUMP {label_end}")

    code.append(f"{label_next}: NOP")
    for elifNode in elifList:
        condE, stmtsE = elifNode[1], elifNode[2]
        label_elif_next = fresh_label()
        code.extend(gen_expr(condE, st))
        code.append(f"JZ {label_elif_next}")
        code.extend(gen_stmt_list(stmtsE, st))
        code.append(f"JUMP {label_end}")
        code.append(f"{label_elif_next}: NOP")

    if elsePart:
        stmtsElse = elsePart[1]
        code.extend(gen_stmt_list(stmtsElse, st))

    code.append(f"{label_end}: NOP")
    return code

def gen_repeat(node, st):
    stmtList, condExpr = node[1], node[2]
    lb_loop = fresh_label()
    code = [f"{lb_loop}: NOP"]
    code.extend(gen_stmt_list(stmtList, st))
    code.extend(gen_expr(condExpr, st))
    code.append(f"JZ {lb_loop}")
    return code

def gen_function_decl(node, st):
    fnName, bodyStmts, retExpr = node[1], node[2], node[3]
    st.add_function(fnName)
    code = [f"{fnName}: NOP"]
    code.extend(gen_stmt_list(bodyStmts, st))
    code.extend(gen_expr(retExpr, st))
    code.append("RETURN")
    return code

def gen_expr(node, st):
    tag = node[0]
    if tag == "binop":
        op = node[1]
        left, right = node[2], node[3]
        code = gen_expr(left, st) + gen_expr(right, st)
        if op == '+':
            code.append("ADD")
        elif op == '-':
            code.append("SUB")
        elif op == '*':
            code.append("MUL")
        elif op == '/':
            code.append("DIV")
        elif op == '>':
            code.append("SUP")
        elif op == '<':
            code.append("INF")
        elif op == '>=':
            code.append("SUPEQ")
        elif op == '<=':
            code.append("INFEQ")
        elif op == '==':
            code.append("EQUAL")
        elif op == '!=':
            code.append("EQUAL")
            code.append("NOT")
        elif op == 'and':
            code.append("AND")
        elif op == 'or':
            code.append("OR")
        return code

    elif tag == "unop":
        code = gen_expr(node[2], st)
        code.append("NOT")
        return code

    elif tag == "number":
        return [f"PUSHI {node[1]}"]

    elif tag == "var":
        varName = node[1]
        varInfo = st.lookup_var(varName)
        offset = varInfo["offset"]
        return [f"PUSHG {offset}"]

    elif tag == "call":
        fnName = node[1]
        st.lookup_function(fnName)
        return [f"PUSHA {fnName}", "CALL"]
