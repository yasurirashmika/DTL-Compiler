"""
Parser - Syntax Analysis
Updated to handle robust data cleaning and NaN values.
"""

from lexer import TokenType, Token
from ast_nodes import *

class Parser:
    """Recursive Descent Parser for DTL"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.program = Program()
    
    def parse(self):
        """Main parsing method - returns AST"""
        while not self._is_at_end():
            # Stop if we hit EOF
            if self._peek().type == TokenType.EOF:
                break
            
            command = self._parse_command()
            if command:
                self.program.add_command(command)
        
        return self.program
    
    def _parse_command(self):
        """Parse a single command based on the starting keyword"""
        token = self._peek()
        
        # Mapping keywords to specific parsing methods
        handlers = {
            TokenType.LOAD: self._parse_load,
            TokenType.SKIP: self._parse_skip,
            TokenType.TRIM: self._parse_trim,
            TokenType.CLEAN: self._parse_clean,
            TokenType.FILLNA: self._parse_fillna,
            TokenType.RENAME: self._parse_rename,
            TokenType.FILTER: self._parse_filter,
            TokenType.SELECT: self._parse_select,
            TokenType.SORT: self._parse_sort,
            TokenType.SAVE: self._parse_save,
            TokenType.GROUP: self._parse_group
        }
        
        handler = handlers.get(token.type)
        if handler:
            return handler()
        else:
            raise SyntaxError(f"Unexpected token {token.type.name} at line {token.line_number}")

    def _parse_load(self):
        self._consume(TokenType.LOAD, "Expected 'load'")
        filename_token = self._consume(TokenType.STRING, "Expected filename string after 'load'")
        return LoadNode(filename_token.value)

    def _parse_skip(self):
        self._consume(TokenType.SKIP, "Expected 'skip'")
        num_token = self._consume(TokenType.NUMBER, "Expected number after 'skip'")
        return SkipNode(int(num_token.value))

    def _parse_trim(self):
        self._consume(TokenType.TRIM, "Expected 'trim'")
        return TrimNode()

    def _parse_clean(self):
        """Parse: clean missing [drop|ffill|bfill] OR clean duplicates"""
        self._consume(TokenType.CLEAN, "Expected 'clean'")
        
        token = self._current_token()
        if token.type == TokenType.MISSING:
            self._advance()
            strategy_token = self._current_token()
            if strategy_token.type in [TokenType.DROP, TokenType.FFILL, TokenType.BFILL]:
                strategy = strategy_token.value.lower()
                self._advance()
                return CleanNode('missing', strategy=strategy)
            else:
                raise SyntaxError(f"Expected drop/ffill/bfill after 'clean missing' at line {strategy_token.line_number}")
        
        elif token.type == TokenType.DUPLICATES:
            self._advance()
            return CleanNode('duplicates', strategy='drop')
        
        raise SyntaxError(f"Expected 'missing' or 'duplicates' after 'clean' at line {token.line_number}")

    def _parse_fillna(self):
        """Parse: fillna column value (Updated for NaN/np.nan)"""
        self._consume(TokenType.FILLNA, "Expected 'fillna'")
        column = self._consume(TokenType.IDENTIFIER, "Expected column name").value
        
        val_token = self._current_token()
        # Accept numbers, strings, or the special np.nan value
        if val_token.type == TokenType.NUMBER:
            value = val_token.value
        elif val_token.type in [TokenType.STRING, TokenType.IDENTIFIER]:
            value = f'"{val_token.value}"'
        else:
            raise SyntaxError(f"Expected value at line {val_token.line_number}")
        
        self._advance()
        return CleanNode('fillna', column=column, value=value)

    def _parse_rename(self):
        self._consume(TokenType.RENAME, "Expected 'rename'")
        old_name = self._consume(TokenType.IDENTIFIER, "Expected old name").value
        self._consume(TokenType.TO, "Expected 'to'")
        new_name = self._consume(TokenType.IDENTIFIER, "Expected new name").value
        return RenameNode(old_name, new_name)

    def _parse_filter(self):
        """Parse: filter column operator value (Updated for NaN support)"""
        self._consume(TokenType.FILTER, "Expected 'filter'")
        column = self._consume(TokenType.IDENTIFIER, "Expected column").value
        
        op_token = self._current_token()
        if op_token.type not in [TokenType.GT, TokenType.LT, TokenType.GTE, TokenType.LTE, TokenType.EQ, TokenType.NEQ]:
            raise SyntaxError(f"Expected operator at line {op_token.line_number}")
        operator = op_token.value
        self._advance()
        
        val_token = self._current_token()
        if val_token.type == TokenType.NUMBER:
            value = val_token.value
        else:
            value = f'"{val_token.value}"'
        
        self._advance()
        return FilterNode(column, operator, value)

    def _parse_select(self):
        self._consume(TokenType.SELECT, "Expected 'select'")
        columns = [self._consume(TokenType.IDENTIFIER, "Expected column").value]
        while self._peek().type == TokenType.COMMA:
            self._consume(TokenType.COMMA, "Expected comma")
            columns.append(self._consume(TokenType.IDENTIFIER, "Expected column").value)
        return SelectNode(columns)

    def _parse_sort(self):
        self._consume(TokenType.SORT, "Expected 'sort'")
        self._consume(TokenType.BY, "Expected 'by'")
        column = self._consume(TokenType.IDENTIFIER, "Expected column").value
        
        order = 'asc'
        if not self._is_at_end() and self._peek().type in [TokenType.ASC, TokenType.DESC]:
            order = self._advance().value.lower()
        return SortNode(column, order)

    def _parse_save(self):
        self._consume(TokenType.SAVE, "Expected 'save'")
        filename = self._consume(TokenType.STRING, "Expected filename").value
        return SaveNode(filename)

    def _parse_group(self):
        self._consume(TokenType.GROUP, "Expected 'group'")
        self._consume(TokenType.BY, "Expected 'by'")
        column = self._consume(TokenType.IDENTIFIER, "Expected group column").value
        
        agg_token = self._current_token()
        if agg_token.type not in [TokenType.SUM, TokenType.AVG, TokenType.COUNT, TokenType.MAX, TokenType.MIN]:
            raise SyntaxError(f"Expected aggregate function at line {agg_token.line_number}")
        agg_func = self._advance().value.lower()
        
        agg_col = self._consume(TokenType.IDENTIFIER, "Expected agg column").value
        return GroupByNode(column, agg_col, agg_func)

    # --- Utility Helpers ---
    def _peek(self):
        return self.tokens[self.current]

    def _current_token(self):
        return self.tokens[self.current]

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def _is_at_end(self):
        return self.current >= len(self.tokens)

    def _consume(self, token_type, error_message):
        if self._is_at_end() or self._current_token().type != token_type:
            line = self._current_token().line_number if not self._is_at_end() else "EOF"
            raise SyntaxError(f"{error_message} at line {line}")
        return self._advance()