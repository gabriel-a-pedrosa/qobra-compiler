# qobra/lexer.py
import sys
import ply.lex as lex

reserved = {
    'int': 'INT',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'elif': 'ELIF',
    'end': 'END',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'read': 'READ',
    'write': 'WRITE',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}

tokens = (
    'IDENTIFIER',
    'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'ASSIGN',   # =
    'GT', 'LT', 'GTE', 'LTE', 'EQ', 'NEQ',
    'LPAR', 'RPAR',  # ( )
    'LBRACE', 'RBRACE',      # { }
    'SEMICOLON',
) + tuple(reserved.values())

# Regex for tokens
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_ASSIGN    = r'='
t_GT        = r'>'
t_LT        = r'<'
t_GTE       = r'>='
t_LTE       = r'<='
t_EQ        = r'=='
t_NEQ       = r'!='
t_LPAR      = r'\('
t_RPAR      = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'//.*'
    pass

def t_error(t):
    print(f"[Lexer Error] Illegal character '{t.value[0]}' (line {t.lexer.lineno}).")
    t.lexer.skip(1)
    sys.exit(1)
    

lexer = lex.lex()
