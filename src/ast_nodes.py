"""
Abstract Syntax Tree Node Definitions
Updated to support robust data cleaning and NaN handling.
"""

class ASTNode:
    """Base class for all AST nodes"""
    pass

class Program(ASTNode):
    """Root node containing the sequence of DTL commands"""
    def __init__(self):
        self.commands = []
    
    def add_command(self, command):
        self.commands.append(command)
    
    def __repr__(self):
        return f"Program(commands={len(self.commands)})"

# --- Data Loading & Structure ---

class LoadNode(ASTNode):
    """Represents: load "filename.csv" """
    def __init__(self, filename):
        self.filename = filename
    
    def __repr__(self):
        return f"LoadNode(filename={self.filename})"

class SaveNode(ASTNode):
    """Represents: save "filename.csv" """
    def __init__(self, filename):
        self.filename = filename
    
    def __repr__(self):
        return f"SaveNode(filename={self.filename})"

# --- Data Cleaning Nodes (Messy Data Support) ---

class CleanNode(ASTNode):
    """
    Represents cleaning operations: 
    - clean missing [drop|ffill|bfill]
    - clean duplicates
    - fillna <col> <val>
    """
    def __init__(self, clean_type, strategy=None, column=None, value=None):
        self.clean_type = clean_type      # 'missing', 'duplicates', or 'fillna'
        self.strategy = strategy          # For missing: 'drop', 'ffill', 'bfill'
        self.column = column              # For fillna: specific column name
        self.value = value                # For fillna: the replacement value (can be 'np.nan')
    
    def __repr__(self):
        return (f"CleanNode(type={self.clean_type}, strategy={self.strategy}, "
                f"col={self.column}, val={self.value})")

class SkipNode(ASTNode):
    """Represents: skip N (skip first N rows)"""
    def __init__(self, num_rows):
        # Ensure num_rows is stored as an integer for code generation
        self.num_rows = int(num_rows)
    
    def __repr__(self):
        return f"SkipNode(rows={self.num_rows})"

class TrimNode(ASTNode):
    """Represents: trim (removes leading/trailing whitespace from strings)"""
    def __repr__(self):
        return "TrimNode()"

# --- Transformation & Analysis Nodes ---

class FilterNode(ASTNode):
    """Represents: filter <column> <operator> <value>"""
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
    
    def __repr__(self):
        return f"FilterNode(column={self.column}, op={self.operator}, value={self.value})"

class RenameNode(ASTNode):
    """Represents: rename <old_col> to <new_col>"""
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
    
    def __repr__(self):
        return f"RenameNode({self.old_name} -> {self.new_name})"

class SelectNode(ASTNode):
    """Represents: select <col1>, <col2>..."""
    def __init__(self, columns):
        self.columns = columns  # A list of strings
    
    def __repr__(self):
        return f"SelectNode(columns={self.columns})"

class SortNode(ASTNode):
    """Represents: sort by <column> [asc|desc]"""
    def __init__(self, column, order='asc'):
        self.column = column
        self.order = order
    
    def __repr__(self):
        return f"SortNode(column={self.column}, order={self.order})"

class GroupByNode(ASTNode):
    """Represents: group by <column> <agg_func> <agg_col>"""
    def __init__(self, column, aggregate_col, aggregate_func):
        self.column = column
        self.aggregate_col = aggregate_col
        self.aggregate_func = aggregate_func # e.g., sum, avg, count
    
    def __repr__(self):
        return (f"GroupByNode(by={self.column}, "
                f"target={self.aggregate_col}, func={self.aggregate_func})")