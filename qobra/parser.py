import sys
import ply.yacc as yacc
from .lexer import tokens


def p_program(p):
    '''program : decl_list stmt_list'''
    p[0] = ("program", p[1], p[2])


def p_decl_list_multiple(p):
    '''decl_list : decl_list decl'''
    p[0] = p[1] + [p[2]]

def p_decl_list_empty(p):
    '''decl_list : '''
    p[0] = []

def p_decl(p):
    '''decl : INT IDENTIFIER SEMICOLON'''
    p[0] = ("decl", p[2])

def p_stmt_list_multiple(p):
    '''stmt_list : stmt_list stmt'''
    p[0] = p[1] + [p[2]]

def p_stmt_list_empty(p):
    '''stmt_list : '''
    p[0] = []

def p_stmt(p):
    '''stmt : assignment SEMICOLON
            | read_stmt SEMICOLON
            | write_stmt SEMICOLON
            | if_stmt
            | repeat_stmt
            | func_decl
    '''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN expr'''
    p[0] = ("assign", p[1], p[3])

def p_read_stmt(p):
    '''read_stmt : READ LPAR IDENTIFIER RPAR'''
    p[0] = ("read", p[3])

def p_write_stmt(p):
    '''write_stmt : WRITE LPAR expr RPAR'''
    p[0] = ("write", p[3])

def p_if_stmt(p):
    '''if_stmt : IF expr THEN stmt_list elif_list else_part END'''
    p[0] = ("if", p[2], p[4], p[5], p[6])

def p_elif_list_multiple(p):
    '''elif_list : elif_list elif_part'''
    p[0] = p[1] + [p[2]]

def p_elif_list_single(p):
    '''elif_list : elif_part'''
    p[0] = [p[1]]

def p_elif_list_empty(p):
    '''elif_list : '''
    p[0] = []

def p_elif_part(p):
    '''elif_part : ELIF expr THEN stmt_list'''
    p[0] = ("elif", p[2], p[4])

def p_else_part(p):
    '''else_part : ELSE stmt_list
                 | '''
    if len(p) == 3:
        p[0] = ("else", p[2])
    else:
        p[0] = None

def p_repeat_stmt(p):
    '''repeat_stmt : REPEAT stmt_list UNTIL expr'''
    p[0] = ("repeat-until", p[2], p[4])

# one rule per precedence level, lowest first: or, and, not, comparison, + -
def p_expr_or(p):
    '''expr : expr OR and_expr'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_expr_to_and(p):
    '''expr : and_expr'''
    p[0] = p[1]

def p_and_expr(p):
    '''and_expr : and_expr AND not_expr'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_and_to_not(p):
    '''and_expr : not_expr'''
    p[0] = p[1]

def p_not_expr(p):
    '''not_expr : NOT not_expr'''
    p[0] = ("unop", "NOT", p[2])

def p_not_to_comparison(p):
    '''not_expr : comparison'''
    p[0] = p[1]

def p_comparison(p):
    '''comparison : arith GT arith
                  | arith LT arith
                  | arith GTE arith
                  | arith LTE arith
                  | arith EQ arith
                  | arith NEQ arith
    '''
    p[0] = ("binop", p[2], p[1], p[3])

def p_comparison_to_arith(p):
    '''comparison : arith'''
    p[0] = p[1]

def p_arith(p):
    '''arith : arith PLUS term
             | arith MINUS term
    '''
    p[0] = ("binop", p[2], p[1], p[3])

def p_arith_to_term(p):
    '''arith : term'''
    p[0] = p[1]

def p_term_binop(p):
    '''term : term TIMES factor
            | term DIVIDE factor
    '''
    p[0] = ("binop", p[2], p[1], p[3])

def p_term_to_factor(p):
    '''term : factor'''
    p[0] = p[1]

def p_factor_paren(p):
    '''factor : LPAR expr RPAR'''
    p[0] = p[2]

def p_factor_number(p):
    '''factor : NUMBER'''
    p[0] = ("number", p[1])

def p_factor_var(p):
    '''factor : IDENTIFIER '''
    p[0] = ("var", p[1])

def p_factor_funccall(p):
    '''factor : IDENTIFIER LPAR RPAR'''
    p[0] = ("call", p[1])

def p_func_decl(p):
    '''func_decl : FUNCTION IDENTIFIER LPAR RPAR LBRACE stmt_list RETURN expr RBRACE'''
    p[0] = ("function_decl", p[2], p[6], p[8])

def p_error(p):
    if p is None:
        print("[Parser Error] Unexpected end of input.")
    else:
        print(f"[Parser Error] Syntax error at '{p.value}' (line {p.lineno}).")
    sys.exit(1)

# Function to reset the lexer line number
def reset_lexer_line(lexer):
    lexer.lineno = 1

# don't write parser.out / parsetab.py
parser = yacc.yacc(write_tables=False, debug=False)
