# DTL Compiler - Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Project Objectives](#project-objectives)
3. [System Architecture](#system-architecture)
4. [Implementation Details](#implementation-details)
5. [Language Specification](#language-specification)
6. [Testing & Results](#testing--results)
7. [Conclusion](#conclusion)

---

## 1. Introduction

### 1.1 Project Aim
The Data Transformation Language (DTL) Compiler is a domain-specific language compiler that translates data transformation commands into executable Python code using the Pandas library. This project demonstrates fundamental compiler design concepts while providing practical utility for data processing tasks.

### 1.2 Motivation
- Bridge the gap between high-level data operations and low-level implementation
- Demonstrate compiler design principles in a practical context
- Create a user-friendly interface for common data transformations
- Provide educational value for understanding compilation phases

### 1.3 Technology Stack
- **Language**: Python 3.x
- **Libraries**: pandas (data manipulation), ply (lexical analysis), re (regex for tokenization)
- **Lexical Analyzer**: PLY (Python Lex-Yacc) - industrial-strength parser generator
- **Design Pattern**: Multi-phase compiler architecture
- **Paradigm**: Object-oriented programming

---

## 2. Project Objectives

### Primary Objectives
1. Design a custom scripting language for data transformations
2. Implement a complete lexical analyzer (tokenizer)
3. Build a parser with Abstract Syntax Tree construction
4. Perform semantic analysis for logical correctness
5. Generate executable Python/Pandas code
6. Test with comprehensive example scripts

### Learning Outcomes
- Understanding of compiler phases
- Practical application of formal languages
- Experience with parser design
- Code generation techniques
- Error handling in compilers

---

## 3. System Architecture

### 3.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DTL COMPILER                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  Source Code │────────▶│    LEXER     │                │
│  │   (.dtl)     │         │  (lexer.py)  │                │
│  └──────────────┘         └──────┬───────┘                │
│                                   │                         │
│                                   ▼ Tokens                  │
│                          ┌──────────────┐                  │
│                          │    PARSER    │                  │
│                          │ (parser.py)  │                  │
│                          └──────┬───────┘                  │
│                                 │                           │
│                                 ▼ AST                       │
│                          ┌──────────────┐                  │
│                          │   SEMANTIC   │                  │
│                          │  ANALYZER    │                  │
│                          │(semantic.py) │                  │
│                          └──────┬───────┘                  │
│                                 │                           │
│                                 ▼ Validated AST            │
│                          ┌──────────────┐                  │
│                          │     CODE     │                  │
│                          │  GENERATOR   │                  │
│                          │ (codegen.py) │                  │
│                          └──────┬───────┘                  │
│                                 │                           │
│                                 ▼                           │
│                          ┌──────────────┐                  │
│                          │ Python Code  │                  │
│                          │  (output.py) │                  │
│                          └──────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Module Descriptions

#### ast_nodes.py
Defines the Abstract Syntax Tree node classes:
- `ASTNode`: Base class for all nodes
- `LoadNode`: Represents file loading
- `FilterNode`: Represents filtering operations
- `SelectNode`: Represents column selection
- `SortNode`: Represents sorting operations
- `SaveNode`: Represents file saving
- `GroupByNode`: Represents grouping and aggregation
- `Program`: Root node containing all commands

#### lexer.py
**Lexical Analyzer** - Breaks source code into tokens
- Token types: Keywords, identifiers, operators, literals
- Pattern matching using regular expressions
- Line-by-line processing
- Error detection for invalid characters

#### parser.py
**Syntax Analyzer** - Validates syntax and builds AST
- Recursive descent parsing strategy
- Grammar rule enforcement
- AST construction
- Syntax error reporting

#### semantic.py
**Semantic Analyzer** - Validates logical correctness
- File existence checking
- Column name validation
- Command sequence validation
- Type checking for operations

#### codegen.py
**Code Generator** - Produces executable Python code
- AST traversal
- Template-based code emission
- Pandas operation mapping
- Comment generation for readability

#### main.py
**Compiler Driver** - Orchestrates all phases
- Command-line interface
- Phase coordination
- Error handling
- User feedback

---

## 4. Implementation Details

### 4.1 Lexical Analysis

#### Token Types
```python
class TokenType(Enum):
    # Keywords
    LOAD, FILTER, SELECT, SORT, BY, SAVE, GROUP
    
    # Literals
    STRING, NUMBER, IDENTIFIER
    
    # Operators
    GT, LT, GTE, LTE, EQ, NEQ  # >, <, >=, <=, ==, !=
    
    # Order
    ASC, DESC
    
    # Aggregates
    SUM, AVG, COUNT, MAX, MIN
    
    # Special
    COMMA, EOF, NEWLINE
```

#### Tokenization Algorithm
1. Read source code line by line
2. Skip empty lines and comments
3. Identify token patterns:
   - Quoted strings for filenames
   - Numbers (integers and floats)
   - Keywords and identifiers
   - Operators and punctuation
4. Create Token objects with type, value, and line number

#### Example
```dtl
load "employees.csv"
```
Tokens:
```
Token(LOAD, 'load', line=1)
Token(STRING, 'employees.csv', line=1)
```

### 4.2 Syntax Analysis

#### Grammar Specification (BNF-like notation)
```
program      → command*
command      → load_cmd | filter_cmd | select_cmd | sort_cmd | save_cmd | group_cmd

load_cmd     → LOAD STRING
filter_cmd   → FILTER IDENTIFIER operator value
select_cmd   → SELECT IDENTIFIER (COMMA IDENTIFIER)*
sort_cmd     → SORT BY IDENTIFIER (ASC | DESC)?
save_cmd     → SAVE STRING
group_cmd    → GROUP BY IDENTIFIER aggregate_func IDENTIFIER

operator     → GT | LT | GTE | LTE | EQ | NEQ
value        → NUMBER | STRING | IDENTIFIER
aggregate_func → SUM | AVG | COUNT | MAX | MIN
```

#### Parser Strategy: Recursive Descent
- Each non-terminal has a parsing method
- Top-down, predictive parsing
- Lookahead of 1 token
- Left-to-right scan

#### AST Construction
Each command creates a corresponding AST node:
```python
# Input: filter age > 25
# Creates: FilterNode(column='age', operator='>', value='25')
```

### 4.3 Semantic Analysis

#### Validation Checks

1. **Structural Validation**
   - Program must start with `load`
   - Commands must be in logical order
   - Program should end with `save`

2. **File Validation**
   - Input file exists
   - Output directory is writable

3. **Column Validation** (optional)
   - Referenced columns exist in dataset
   - Aggregate operations use numeric columns

4. **Operator Validation**
   - Comparison operators are valid
   - Aggregate functions are recognized

#### Error Reporting
```
=== SEMANTIC ANALYSIS REPORT ===

ERRORS (2):
  - Column 'salary' does not exist in loaded data
  - Output directory does not exist: invalid/path

WARNINGS (1):
  - Program has no 'save' command - results won't be saved
```

### 4.4 Code Generation

#### Generation Strategy
1. Traverse AST in order
2. For each node, emit corresponding Pandas code
3. Add comments for readability
4. Include print statements for feedback

#### Code Templates

**Load Command:**
```python
df = pd.read_csv("filename.csv")
print(f"Loaded {len(df)} rows from filename.csv")
```

**Filter Command:**
```python
df = df[df["column"] > value]
print(f"After filter: {len(df)} rows remaining")
```

**Select Command:**
```python
df = df[["col1", "col2"]]
print(f"Selected 2 columns")
```

**Sort Command:**
```python
df = df.sort_values(by="column", ascending=False)
print(f"Sorted by column (desc)")
```

**Save Command:**
```python
df.to_csv("output.csv", index=False)
print(f"Saved {len(df)} rows to output.csv")
```

---

## 5. Language Specification

### 5.1 Lexical Elements

#### Keywords (case-insensitive)
```
load, filter, select, sort, by, save, group
asc, desc
sum, avg, count, max, min
```

#### Identifiers
- Start with letter or underscore
- Contains letters, digits, underscores
- Examples: `age`, `employee_name`, `salary_2023`

#### Literals
- **Strings**: Enclosed in double quotes `"file.csv"`
- **Numbers**: Integers or floats `25`, `3.14`, `-100`

#### Operators
```
>   (greater than)
<   (less than)
>=  (greater than or equal)
<=  (less than or equal)
==  (equal)
!=  (not equal)
```

#### Punctuation
```
,   (comma for separating columns)
```

#### Comments
```
# This is a comment (ignored by compiler)
```

### 5.2 Syntax Rules

#### Command Structure
Each command occupies a single line (or continues with proper formatting).

#### Type System
- **Numeric types**: Used in comparisons, aggregations
- **String types**: File names, column names
- **Boolean results**: From filter conditions

### 5.3 Semantic Rules

1. **Load First**: Program must begin with `load`
2. **Column Consistency**: Selected/filtered columns must exist
3. **File Paths**: Must be valid relative or absolute paths
4. **Aggregate Constraints**: Aggregation requires grouping

---

## 6. Testing & Results

### 6.1 Test Cases

#### Test 1: Basic Filtering
**Input (example1.dtl):**
```dtl
load "test_data/employees.csv"
filter salary > 70000
select name, department, salary
sort by salary desc
save "test_data/high_salary_employees.csv"
```

**Expected Behavior:**
- Load 15 employee records
- Filter to 8 employees with salary > 70000
- Select 3 columns
- Sort by salary descending
- Save results

**Output:**
```
Loaded 15 rows from test_data/employees.csv
After filter: 8 rows remaining
Selected 3 columns
Sorted by salary (desc)
Saved 8 rows to test_data/high_salary_employees.csv
Data transformation completed successfully!
```

#### Test 2: Complex Filtering
**Input (example2.dtl):**
```dtl
load "test_data/employees.csv"
filter department == Engineering
filter age < 35
filter experience >= 2
select name, age, salary, experience
sort by experience desc
save "test_data/young_engineers.csv"
```

**Expected Behavior:**
- Multiple filter conditions
- String comparison
- Numeric range checks

#### Test 3: Aggregation
**Input (example3.dtl):**
```dtl
load "test_data/employees.csv"
select department, salary
group by department avg salary
sort by salary desc
save "test_data/dept_avg_salary.csv"
```

**Expected Output:**
| department  | salary   |
|------------|----------|
| Engineering| 85000.00 |
| Marketing  | 71666.67 |
| Sales      | 71250.00 |

### 6.2 Error Handling Tests

#### Syntax Error
```dtl
load "file.csv"
filter age >  # Missing value
```
**Error:** `Expected value after operator at line 2`

#### Semantic Error
```dtl
load "nonexistent.csv"
```
**Error:** `File not found: nonexistent.csv`

#### Column Error
```dtl
load "test.csv"
filter invalid_column > 5
```
**Error:** `Column 'invalid_column' does not exist in loaded data`

### 6.3 Performance Analysis

#### Compilation Time
- Small scripts (5-10 commands): < 0.1 seconds
- Large scripts (50+ commands): < 0.5 seconds

#### Generated Code Quality
- Clean, readable Python code
- Efficient Pandas operations
- No redundant computations

---

## 7. Conclusion

### 7.1 Achievements

**Complete Compiler Implementation**
- All four phases working correctly
- Clean separation of concerns
- Modular, maintainable code

**Practical Utility**
- Generates working Python scripts
- Simplifies data transformation tasks
- User-friendly DSL syntax

**Educational Value**
- Demonstrates compiler concepts
- Real-world application
- Extensible design

### 7.2 Challenges & Solutions

**Challenge 1: Token Ambiguity**
- Problem: Distinguishing between keywords and identifiers
- Solution: Case-insensitive keyword matching with fallback

**Challenge 2: Error Recovery**
- Problem: Graceful error handling
- Solution: Comprehensive try-catch with informative messages

**Challenge 3: AST Design**
- Problem: Representing different command types
- Solution: Object-oriented hierarchy with base ASTNode class

### 7.3 Future Enhancements

1. **JOIN Operations**: Merge multiple datasets
2. **Computed Columns**: Add expressions like `salary * 1.1`
3. **User-Defined Functions**: Custom transformations
4. **Optimization**: Dead code elimination, constant folding
5. **Interactive Mode**: REPL for testing commands
6. **Better Error Messages**: Line numbers, suggestions
7. **Type System**: Static type checking
8. **Excel Support**: Read/write .xlsx files

### 7.4 Lessons Learned

- **Compiler phases are interdependent**: Good lexer design simplifies parsing
- **Error messages matter**: Clear errors improve user experience
- **Testing is crucial**: Edge cases reveal design flaws
- **Modularity pays off**: Separate files make debugging easier
- **Documentation is essential**: Good docs make projects accessible

### 7.5 Academic Relevance

This project covers:
- **Formal Languages**: Grammar specification, syntax rules
- **Automata Theory**: Token recognition patterns
- **Data Structures**: Trees (AST), symbol tables
- **Algorithm Design**: Recursive descent parsing
- **Software Engineering**: Modular design, testing

### 7.6 Final Thoughts

The DTL Compiler successfully demonstrates that compiler design concepts can be applied to solve real-world problems. By creating a domain-specific language for data transformations, we've built a tool that is both educationally valuable and practically useful.

The project shows that a complete compiler can be built in a week with proper planning, modular design, and focus on essential features. The source-to-source compilation approach (transpiling to Python) allowed us to skip low-level details while still demonstrating core compiler concepts.

---

## Appendix A: Complete Example

### Input Script
```dtl
# Analyze high-performing employees
load "test_data/employees.csv"
filter experience >= 5
filter salary > 65000
select name, department, salary, experience
sort by salary desc
save "test_data/top_performers.csv"
```

### Generated Python Code
```python
# Auto-generated Python code from DTL Compiler
# Date: 2025-02-11 14:30:00

import pandas as pd

# Load data from test_data/employees.csv
df = pd.read_csv("test_data/employees.csv")
print(f"Loaded {len(df)} rows from test_data/employees.csv")

# Filter: experience >= 5
df = df[df["experience"] >= 5]
print(f"After filter: {len(df)} rows remaining")

# Filter: salary > 65000
df = df[df["salary"] > 65000]
print(f"After filter: {len(df)} rows remaining")

# Select columns: name, department, salary, experience
df = df[["name", "department", "salary", "experience"]]
print(f"Selected 4 columns")

# Sort by salary (desc)
df = df.sort_values(by="salary", ascending=False)
print(f"Sorted by salary (desc)")

# Save results to test_data/top_performers.csv
df.to_csv("test_data/top_performers.csv", index=False)
print(f"Saved {len(df)} rows to test_data/top_performers.csv")

print("Data transformation completed successfully!")
```

---

**End of Documentation**