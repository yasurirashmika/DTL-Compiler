"""
Code Generator - Converts AST to executable Python code.
COMPLETELY FIXED: 
- Skip command now uses skiprows parameter in pd.read_csv (not iloc after loading)
- Updated pandas 2.0+ syntax
"""

import os
from ast_nodes import *

class CodeGenerator:
    """Generates Python code from the AST"""
    
    def __init__(self, ast):
        self.ast = ast
        self.code_lines = []
        self.imports_added = set()
        self.df_var = 'df'
        self.skip_rows = 0  # Track skip rows for load command
    
    def generate(self):
        """Generate complete Python code from AST"""
        self._add_imports()
        self._preprocess_skip()  # Find skip commands before generating
        self._generate_commands()
        return '\n'.join(self.code_lines)
    
    def save_to_file(self, filename):
        """Generate code and save to file"""
        code = self.generate()
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w') as f:
            f.write(code)
        return code
    
    def _add_imports(self):
        """Add necessary imports"""
        self.code_lines.append("import pandas as pd")
        self.code_lines.append("import numpy as np")
        self.code_lines.append("import warnings")
        self.code_lines.append("warnings.filterwarnings('ignore')")
        self.code_lines.append("")
    
    def _preprocess_skip(self):
        """Find skip command that comes right after load"""
        for i, command in enumerate(self.ast.commands):
            if isinstance(command, LoadNode):
                # Check if next command is skip
                if i + 1 < len(self.ast.commands) and isinstance(self.ast.commands[i + 1], SkipNode):
                    self.skip_rows = self.ast.commands[i + 1].num_rows
                break
    
    def _generate_commands(self):
        """Generate code for each command in the AST"""
        for i, command in enumerate(self.ast.commands):
            if isinstance(command, LoadNode):
                self._gen_load(command)
            elif isinstance(command, SkipNode):
                # Skip is handled in load command, just add a comment
                self.code_lines.append(f"# Skip handled in load (skiprows={self.skip_rows})")
                self.code_lines.append("")
            elif isinstance(command, SaveNode):
                self._gen_save(command)
            elif isinstance(command, FilterNode):
                self._gen_filter(command)
            elif isinstance(command, SelectNode):
                self._gen_select(command)
            elif isinstance(command, SortNode):
                self._gen_sort(command)
            elif isinstance(command, GroupByNode):
                self._gen_group_by(command)
            elif isinstance(command, CleanNode):
                self._gen_clean(command)
            elif isinstance(command, TrimNode):
                self._gen_trim(command)
            elif isinstance(command, RenameNode):
                self._gen_rename(command)
    
    def _gen_load(self, node):
        """Generate load statement with skiprows if needed"""
        filename = self._clean_string(node.filename)
        self.code_lines.append(f"# Load data from CSV")
        
        # CRITICAL FIX: Use skiprows parameter in read_csv
        if self.skip_rows > 0:
            self.code_lines.append(
                f"{self.df_var} = pd.read_csv('{filename}', "
                f"skiprows={self.skip_rows}, on_bad_lines='skip', engine='python')"
            )
            self.code_lines.append(f"print(f'Loaded {{len({self.df_var})}} rows (skipped first {self.skip_rows} header rows)')")
        else:
            self.code_lines.append(
                f"{self.df_var} = pd.read_csv('{filename}', on_bad_lines='skip', engine='python')"
            )
            self.code_lines.append(f"print(f'Loaded {{len({self.df_var})}} rows')")
        self.code_lines.append("")
    
    def _gen_save(self, node):
        """Generate save statement"""
        filename = self._clean_string(node.filename)
        self.code_lines.append(f"# Save results to CSV")
        self.code_lines.append(f"{self.df_var}.to_csv('{filename}', index=False)")
        self.code_lines.append(f"print(f'Data saved to {filename}')")
        self.code_lines.append("")
    
    def _gen_filter(self, node):
        """Generate filter statement"""
        column = self._clean_string(node.column)
        operator = node.operator
        value = node.value
        
        # Handle comparison operators
        op_map = {'==': '==', '!=': '!=', '>': '>', '<': '<', '>=': '>=', '<=': '<='}
        py_op = op_map.get(operator, '==')
        
        # Clean up value (remove extra quotes if present)
        if isinstance(value, str) and (value.startswith('"') or value.startswith("'")):
            value = value.strip('"').strip("'")
            value = f"'{value}'"
        
        self.code_lines.append(f"# Filter: {column} {operator} {value}")
        self.code_lines.append(f"{self.df_var} = {self.df_var}[{self.df_var}['{column}'] {py_op} {value}]")
        self.code_lines.append(f"print(f'After filter: {{len({self.df_var})}} rows')")
        self.code_lines.append("")
    
    def _gen_select(self, node):
        """Generate select statement"""
        columns = [f"'{self._clean_string(col)}'" for col in node.columns]
        self.code_lines.append(f"# Select columns")
        self.code_lines.append(f"{self.df_var} = {self.df_var}[[{', '.join(columns)}]]")
        self.code_lines.append(f"print(f'Selected {{len({self.df_var}.columns)}} columns')")
        self.code_lines.append("")
    
    def _gen_sort(self, node):
        """Generate sort statement"""
        column = self._clean_string(node.column)
        ascending = node.order.lower() == 'asc'
        self.code_lines.append(f"# Sort by {column} ({node.order})")
        self.code_lines.append(f"{self.df_var} = {self.df_var}.sort_values(by='{column}', ascending={ascending})")
        self.code_lines.append(f"{self.df_var} = {self.df_var}.reset_index(drop=True)")
        self.code_lines.append(f"print(f'Sorted by {column}')")
        self.code_lines.append("")
    
    def _gen_group_by(self, node):
        """Generate group by statement"""
        by_col = self._clean_string(node.column)
        agg_col = self._clean_string(node.aggregate_col)
        agg_func = node.aggregate_func.lower()
        
        func_map = {'sum': 'sum', 'avg': 'mean', 'count': 'count', 'max': 'max', 'min': 'min'}
        py_func = func_map.get(agg_func, 'sum')
        
        self.code_lines.append(f"# Group by {by_col} and {agg_func} {agg_col}")
        self.code_lines.append(f"{self.df_var} = {self.df_var}.groupby('{by_col}')['{agg_col}'].{py_func}().reset_index()")
        self.code_lines.append(f"{self.df_var}.columns = ['{by_col}', '{agg_col}_{py_func}']")
        self.code_lines.append(f"print(f'Grouped by {by_col}')")
        self.code_lines.append("")
    
    def _gen_clean(self, node):
        """Generate clean statement - with pandas 2.0+ syntax"""
        if node.clean_type == 'missing':
            if node.strategy == 'drop':
                self.code_lines.append(f"# Drop rows with any missing values")
                self.code_lines.append(f"{self.df_var} = {self.df_var}.dropna()")
            elif node.strategy == 'ffill':
                self.code_lines.append(f"# Forward fill missing values")
                self.code_lines.append(f"{self.df_var} = {self.df_var}.ffill()")
            elif node.strategy == 'bfill':
                self.code_lines.append(f"# Backward fill missing values")
                self.code_lines.append(f"{self.df_var} = {self.df_var}.bfill()")
            self.code_lines.append(f"print(f'After cleaning: {{len({self.df_var})}} rows')")
        elif node.clean_type == 'duplicates':
            self.code_lines.append(f"# Remove duplicate rows")
            self.code_lines.append(f"{self.df_var} = {self.df_var}.drop_duplicates()")
            self.code_lines.append(f"print(f'After removing duplicates: {{len({self.df_var})}} rows')")
        elif node.clean_type == 'fillna':
            column = self._clean_string(node.column)
            value = node.value
            self.code_lines.append(f"# Fill missing values in '{column}'")
            self.code_lines.append(f"if '{column}' in {self.df_var}.columns:")
            if value == 'np.nan':
                self.code_lines.append(f"    {self.df_var}['{column}'] = np.nan")
            else:
                # Clean up the value (remove extra quotes)
                value_clean = value.strip('"').strip("'")
                # Check if it's a number
                try:
                    float(value_clean)
                    fill_value = value_clean
                except ValueError:
                    fill_value = f"'{value_clean}'"
                self.code_lines.append(f"    {self.df_var}['{column}'] = {self.df_var}['{column}'].fillna({fill_value})")
            self.code_lines.append(f"else:")
            self.code_lines.append(f"    print(f\"Warning: Column '{column}' not found in dataframe\")")
        self.code_lines.append("")
    
    def _gen_trim(self, node):
        """Generate trim statement for string columns"""
        self.code_lines.append(f"# Trim whitespace from all string columns")
        self.code_lines.append(f"for col in {self.df_var}.select_dtypes(include=['object', 'string']).columns:")
        self.code_lines.append(f"    if {self.df_var}[col].dtype == 'object':")
        self.code_lines.append(f"        {self.df_var}[col] = {self.df_var}[col].astype(str).str.strip()")
        self.code_lines.append(f"print('Trimmed whitespace from string columns')")
        self.code_lines.append("")
    
    def _gen_rename(self, node):
        """Generate rename statement"""
        old_name = self._clean_string(node.old_name)
        new_name = self._clean_string(node.new_name)
        self.code_lines.append(f"# Rename column '{old_name}' to '{new_name}'")
        self.code_lines.append(f"if '{old_name}' in {self.df_var}.columns:")
        self.code_lines.append(f"    {self.df_var} = {self.df_var}.rename(columns={{'{old_name}': '{new_name}'}})")
        self.code_lines.append(f"else:")
        self.code_lines.append(f"    print(f\"Warning: Column '{old_name}' not found\")")
        self.code_lines.append("")
    
    def _clean_string(self, s):
        """Remove quotes from string if present"""
        if isinstance(s, str):
            return s.strip('"').strip("'")
        return str(s)


# Test the code generator
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    test_code = """
    load "test.csv"
    skip 2
    trim
    clean missing drop
    clean duplicates
    fillna age 0
    select name, age, salary
    filter salary > 70000
    sort by salary desc
    save "output.csv"
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator(ast)
    print(codegen.generate())