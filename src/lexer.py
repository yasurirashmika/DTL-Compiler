"""
Lexical Analyzer (Lexer/Tokenizer)
Updated to handle NaN and messy data literals.
"""

import re
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

class Lexer:
    KEYWORDS = {
        'load': TokenType.LOAD, 'filter': TokenType.FILTER, 'select': TokenType.SELECT,
        'sort': TokenType.SORT, 'by': TokenType.BY, 'save': TokenType.SAVE,
        'group': TokenType.GROUP, 'asc': TokenType.ASC, 'desc': TokenType.DESC,
        'sum': TokenType.SUM, 'avg': TokenType.AVG, 'count': TokenType.COUNT,
        'max': TokenType.MAX, 'min': TokenType.MIN, 'clean': TokenType.CLEAN,
        'fillna': TokenType.FILLNA, 'skip': TokenType.SKIP, 'trim': TokenType.TRIM,
        'rename': TokenType.RENAME, 'missing': TokenType.MISSING, 'duplicates': TokenType.DUPLICATES,
        'drop': TokenType.DROP, 'ffill': TokenType.FFILL, 'bfill': TokenType.BFILL, 'to': TokenType.TO
    }

    OPERATORS = {
        '>': TokenType.GT, '<': TokenType.LT, '>=': TokenType.GTE,
        '<=': TokenType.LTE, '==': TokenType.EQ, '!=': TokenType.NEQ
    }

    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.current_line = 1

    def tokenize(self):
        lines = self.source.split('\n')
        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            line = line.strip()
            if not line or line.startswith('#'): continue
            self._tokenize_line(line)
        self.tokens.append(Token(TokenType.EOF, None, self.current_line))
        return self.tokens

    def _tokenize_line(self, line):
        i = 0
        while i < len(line):
            if line[i].isspace():
                i += 1; continue
            
            # String literals
            if line[i] in ['"', "'"]:
                quote = line[i]; i += 1; start = i
                while i < len(line) and line[i] != quote: i += 1
                self.tokens.append(Token(TokenType.STRING, line[start:i], self.current_line))
                i += 1; continue

            # Numbers
            if line[i].isdigit() or (line[i] == '-' and i + 1 < len(line) and line[i+1].isdigit()):
                start = i
                if line[i] == '-': i += 1
                while i < len(line) and (line[i].isdigit() or line[i] == '.'): i += 1
                self.tokens.append(Token(TokenType.NUMBER, line[start:i], self.current_line))
                continue

            # Identifiers & NaN Handling (Fixes "Unexpected token N")
            if line[i].isalpha() or line[i] == '_':
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'): i += 1
                word = line[start:i]
                if word == "NaN":
                    self.tokens.append(Token(TokenType.NUMBER, "np.nan", self.current_line))
                else:
                    t_type = self.KEYWORDS.get(word.lower(), TokenType.IDENTIFIER)
                    self.tokens.append(Token(t_type, word, self.current_line))
                continue

            # Multi-char Operators
            if i + 1 < len(line) and line[i:i+2] in self.OPERATORS:
                self.tokens.append(Token(self.OPERATORS[line[i:i+2]], line[i:i+2], self.current_line))
                i += 2; continue
            
            # Single-char Operators & Punctuation
            if line[i] in self.OPERATORS:
                self.tokens.append(Token(self.OPERATORS[line[i]], line[i], self.current_line))
                i += 1; continue
            if line[i] == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.current_line))
                i += 1; continue

            raise SyntaxError(f"Unknown character '{line[i]}' at line {self.current_line}")