"""
Semantic Analyzer
Validates logical correctness of the program
- Checks if files exist
- Validates column names (if data is loaded)
- Ensures proper command sequence
ENHANCED: Detects filter-after-select conflicts
FIXED: Respects skip commands when validating columns
"""

import os
import pandas as pd
from ast_nodes import *


class SemanticAnalyzer:
    """Validates semantic correctness of AST"""
    
    def __init__(self, ast, validate_files=True, validate_columns=True):
        self.ast = ast
        self.validate_files = validate_files
        self.validate_columns = validate_columns
        self.errors = []
        self.warnings = []
        
        # Track state during analysis
        self.current_file = None
        self.current_columns = None
        self.has_load = False
        self.has_save = False
        self.selected_columns = None  # Track which columns are selected
    
    def analyze(self):
        """Perform semantic analysis"""
        if not self.ast.commands:
            self.errors.append("Empty program - no commands found")
            return False
        
        # Pre-pass: detect filter-after-select issues
        self._check_filter_select_ordering()
        
        # Check command sequence
        for i, command in enumerate(self.ast.commands):
            self._analyze_command(command, i)
        
        # Validate overall structure
        if not self.has_load:
            self.errors.append("Program must start with a 'load' command")
        
        if not self.has_save:
            self.warnings.append("Program has no 'save' command - results won't be saved")
        
        # Return True if no errors
        return len(self.errors) == 0
    
    def _check_filter_select_ordering(self):
        """Scan for filter commands that reference columns removed by select"""
        last_select_idx = -1
        selected_cols = set()
        
        for i, cmd in enumerate(self.ast.commands):
            if isinstance(cmd, SelectNode):
                last_select_idx = i
                selected_cols = set(cmd.columns)
            elif isinstance(cmd, FilterNode):
                if last_select_idx >= 0 and cmd.column not in selected_cols:
                    self.warnings.append(
                        f"Command at position {i + 1}: Filter on '{cmd.column}' may fail because "
                        f"'select' at position {last_select_idx + 1} doesn't include this column. "
                        f"Consider filtering before selecting columns, or include '{cmd.column}' in select."
                    )
    
    def _analyze_command(self, command, index):
        """Map commands to specific analysis methods"""
        method_map = {
            LoadNode: self._analyze_load,
            SkipNode: self._analyze_skip,
            TrimNode: self._analyze_trim,
            CleanNode: self._analyze_clean,
            RenameNode: self._analyze_rename,
            FilterNode: self._analyze_filter,
            SelectNode: self._analyze_select,
            SortNode: self._analyze_sort,
            SaveNode: self._analyze_save,
            GroupByNode: self._analyze_group
        }
        
        handler = method_map.get(type(command))
        if handler:
            handler(command, index)

    def _analyze_load(self, node, index):
        """Validate load command and read headers robustly - FIXED to respect skip"""
        if index != 0:
            self.warnings.append(f"'load' should be the first command (found at position {index + 1})")
        
        self.has_load = True
        self.current_file = node.filename
        
        if self.validate_files and not os.path.exists(node.filename):
            self.errors.append(f"File not found: {node.filename}")
            return
        
        if self.validate_columns:
            try:
                # ✅ FIXED: Check for skip commands that come AFTER this load
                skip_rows = 0
                for i, cmd in enumerate(self.ast.commands):
                    if i > index:  # Only look at commands after load
                        break
                    # Actually, skip comes AFTER load in the script, so check commands after load
                # Correct approach: look ahead for skip commands
                for i in range(index + 1, len(self.ast.commands)):
                    cmd = self.ast.commands[i]
                    if isinstance(cmd, SkipNode):
                        skip_rows = cmd.num_rows
                        break  # Only use the first skip after load
                    elif not isinstance(cmd, (TrimNode, CleanNode)):
                        # Stop looking if we hit a command that modifies structure
                        break
                
                # Read CSV with skiprows parameter
                df = pd.read_csv(
                    node.filename, 
                    nrows=0, 
                    skiprows=skip_rows if skip_rows > 0 else None,
                    on_bad_lines='skip', 
                    engine='python'
                )
                self.current_columns = set(df.columns)
                self.selected_columns = None  # Reset selected columns
            except Exception as e:
                self.errors.append(f"Cannot read headers from {node.filename}: {str(e)}")

    def _analyze_skip(self, node, index):
        """Validate skip command"""
        if not self.has_load:
            self.errors.append(f"'skip' at position {index + 1} used before 'load'")

    def _analyze_trim(self, node, index):
        """Validate trim command"""
        if not self.has_load:
            self.errors.append(f"'trim' at position {index + 1} used before 'load'")

    def _analyze_clean(self, node, index):
        """Validate clean command"""
        if not self.has_load:
            self.errors.append(f"'clean' at position {index + 1} used before 'load'")
        
        if node.clean_type == 'missing':
            if node.strategy not in ['drop', 'ffill', 'bfill']:
                self.errors.append(f"Invalid strategy '{node.strategy}' for clean missing")
        elif node.clean_type == 'duplicates':
            pass  # duplicates is always valid
        elif node.clean_type == 'fillna':
            if self.validate_columns and self.current_columns:
                if node.column not in self.current_columns:
                    self.warnings.append(f"'fillna' for column '{node.column}' - column may not exist at this point")

    def _analyze_rename(self, node, index):
        """Validate rename command"""
        if not self.has_load:
            self.errors.append(f"'rename' at position {index + 1} used before 'load'")
        
        if self.validate_columns and self.current_columns:
            if node.old_name not in self.current_columns:
                self.errors.append(f"Cannot rename '{node.old_name}' - column does not exist")
            else:
                # Update current columns: remove old, add new
                self.current_columns = set([node.new_name if c == node.old_name else c for c in self.current_columns])

    def _analyze_filter(self, node, index):
        """Validate filter column, operator, and NaN values"""
        if not self.has_load:
            self.errors.append(f"'filter' at position {index + 1} used before 'load'")
            return

        # Check if column exists in current available columns
        cols_to_check = self.selected_columns if self.selected_columns else self.current_columns
        if self.validate_columns and cols_to_check:
            if node.column not in cols_to_check:
                self.errors.append(
                    f"Column '{node.column}' not available at filter position {index + 1}. "
                    f"Available columns: {', '.join(sorted(cols_to_check))}"
                )

        valid_operators = ['>', '<', '>=', '<=', '==', '!=']
        if node.operator not in valid_operators:
            self.errors.append(f"Invalid operator '{node.operator}'")

    def _analyze_select(self, node, index):
        """Validate select command and track selected columns"""
        if not self.has_load:
            self.errors.append(f"'select' at position {index + 1} used before 'load'")
        
        # Validate columns exist
        if self.validate_columns and self.current_columns:
            for col in node.columns:
                if col not in self.current_columns:
                    self.errors.append(f"Column '{col}' does not exist in loaded data")
        
        # Track selected columns for downstream validation
        self.selected_columns = set(node.columns)

    def _analyze_sort(self, node, index):
        """Validate sort command"""
        if not self.has_load:
            self.errors.append(f"'sort' at position {index + 1} used before 'load'")
        
        # Check against available columns
        cols_to_check = self.selected_columns if self.selected_columns else self.current_columns
        if self.validate_columns and cols_to_check:
            if node.column not in cols_to_check:
                self.errors.append(
                    f"Cannot sort by '{node.column}' - column not available at this point. "
                    f"Available columns: {', '.join(sorted(cols_to_check))}"
                )
        
        # Validate order
        if node.order not in ['asc', 'desc']:
            self.errors.append(f"Invalid sort order '{node.order}' - must be 'asc' or 'desc'")

    def _analyze_save(self, node, index):
        """Validate save command"""
        if not self.has_load:
            self.errors.append(f"'save' at position {index + 1} used before 'load'")
        
        self.has_save = True
        
        # Check if output directory exists
        if self.validate_files:
            output_dir = os.path.dirname(node.filename)
            if output_dir and not os.path.exists(output_dir):
                self.warnings.append(f"Output directory may not exist: {output_dir}")

    def _analyze_group(self, node, index):
        """Validate group by command"""
        if not self.has_load:
            self.errors.append(f"'group' at position {index + 1} used before 'load'")
        
        # Check available columns
        cols_to_check = self.selected_columns if self.selected_columns else self.current_columns
        if self.validate_columns and cols_to_check:
            if node.column not in cols_to_check:
                self.errors.append(f"Cannot group by '{node.column}' - column not available")
            if node.aggregate_col not in cols_to_check:
                self.errors.append(f"Cannot aggregate '{node.aggregate_col}' - column not available")
        
        # Validate aggregate function
        valid_funcs = ['sum', 'avg', 'count', 'max', 'min']
        if node.aggregate_func not in valid_funcs:
            self.errors.append(f"Invalid aggregate function '{node.aggregate_func}'")
    
    def print_report(self):
        """Print analysis report"""
        print("\n=== SEMANTIC ANALYSIS REPORT ===")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ No errors or warnings - program is semantically correct!")
        
        return len(self.errors) == 0


# Test semantic analyzer
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    test_code = """
    load "test.csv"
    skip 2
    filter age > 25
    select name, salary
    save "output.csv"
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Analyze without file validation for testing
    analyzer = SemanticAnalyzer(ast, validate_files=False, validate_columns=False)
    is_valid = analyzer.analyze()
    analyzer.print_report()