"""
Lexical Analyzer (Lexer/Tokenizer) using PLY
Updated to handle NaN and messy data literals.
"""

import ply.lex as lex
from enum import Enum

class TokenType(Enum):
    # Original Keywords
    LOAD = "LOAD"; FILTER = "FILTER"; SELECT = "SELECT"; SORT = "SORT"
    BY = "BY"; SAVE = "SAVE"; GROUP = "GROUP"

    # Cleaning keywords
    CLEAN = "CLEAN"; FILLNA = "FILLNA"; SKIP = "SKIP"; TRIM = "TRIM"
    RENAME = "RENAME"; MISSING = "MISSING"; DUPLICATES = "DUPLICATES"
    DROP = "DROP"; FFILL = "FFILL"; BFILL = "BFILL"; TO = "TO"

    # Literals
    STRING = "STRING"; NUMBER = "NUMBER"; IDENTIFIER = "IDENTIFIER"

    # Operators
    GT = "GT"; LT = "LT"; GTE = "GTE"; LTE = "LTE"; EQ = "EQ"; NEQ = "NEQ"

    # Order keywords
    ASC = "ASC"; DESC = "DESC"

    # Aggregate functions
    SUM = "SUM"; AVG = "AVG"; COUNT = "COUNT"; MAX = "MAX"; MIN = "MIN"

    # Punctuation & Special
    COMMA = "COMMA"; EOF = "EOF"; NEWLINE = "NEWLINE"

class Token:
    def __init__(self, token_type, value, line_number):
        self.type = token_type
        self.value = value
        self.line_number = line_number

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line_number})"

# PLY Lexer implementation
tokens = [
    'STRING', 'NUMBER', 'IDENTIFIER',
    'GT', 'LT', 'GTE', 'LTE', 'EQ', 'NEQ',
    'COMMA', 'NEWLINE'
]

# Reserved words
reserved = {
    'load': 'LOAD', 'filter': 'FILTER', 'select': 'SELECT',
    'sort': 'SORT', 'by': 'BY', 'save': 'SAVE',
    'group': 'GROUP', 'asc': 'ASC', 'desc': 'DESC',
    'sum': 'SUM', 'avg': 'AVG', 'count': 'COUNT',
    'max': 'MAX', 'min': 'MIN', 'clean': 'CLEAN',
    'fillna': 'FILLNA', 'skip': 'SKIP', 'trim': 'TRIM',
    'rename': 'RENAME', 'missing': 'MISSING', 'duplicates': 'DUPLICATES',
    'drop': 'DROP', 'ffill': 'FFILL', 'bfill': 'BFILL', 'to': 'TO'
}

tokens += list(reserved.values())

# Token definitions
t_GT = r'>'
t_LT = r'<'
t_GTE = r'>='
t_LTE = r'<='
t_EQ = r'=='
t_NEQ = r'!='
t_COMMA = r','

def t_STRING(t):
    r'"[^"]*"|\'[^"]*\''
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_NUMBER(t):
    r'-?\d+(\.\d+)?'
    if t.value == '-':
        t.type = 'IDENTIFIER'  # Handle lone minus as identifier
    else:
        try:
            t.value = float(t.value)
        except ValueError:
            t.type = 'IDENTIFIER'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    if t.value.lower() == 'nan':
        t.type = 'NUMBER'
        t.value = 'np.nan'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# Ignored characters
t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer_obj = lex.lex()

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.current_line = 1

    def tokenize(self):
        # Preprocess: remove comments and empty lines
        lines = []
        for line in self.source.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            lines.append(line)
        processed_source = '\n'.join(lines)
        
        lexer_obj.input(processed_source)
        self.tokens = []
        while True:
            tok = lexer_obj.token()
            if not tok:
                break
            # Skip NEWLINE tokens as the parser doesn't expect them
            if tok.type == 'NEWLINE':
                continue
            # Convert PLY token to our Token class
            token_type = TokenType[tok.type]
            token = Token(token_type, tok.value, tok.lineno)
            self.tokens.append(token)
        self.tokens.append(Token(TokenType.EOF, None, self.current_line))
        return self.tokens
    
    def print_tokens(self):
        """Prints the list of tokens generated during tokenization"""
        print(f"\n[Lexer] Tokenized {len(self.tokens)} items:")
        print("-" * 50)
        # Use headers to make the output clear in the console
        print(f"{'TYPE':<15} {'VALUE':<20} {'LINE'}")
        print("-" * 50)
        for token in self.tokens:
            # Format the output for professional display during demo
            type_str = token.type.name
            val_str = str(token.value)
            print(f"{type_str:<15} {val_str:<20} {token.line_number}")
        print("-" * 50 + "\n")