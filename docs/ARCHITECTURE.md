# DTL Compiler Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DTL COMPILER SYSTEM                            │
│                                                                       │
│  Input: example.dtl (Data Transformation Language Script)            │
│  Output: generated_output.py (Executable Python/Pandas Code)         │
└─────────────────────────────────────────────────────────────────────┘


                            ┌─────────────────┐
                            │  DTL Script     │
                            │  (.dtl file)    │
                            └────────┬────────┘
                                     │
                                     │ Text Source Code
                                     ▼
        ┌────────────────────────────────────────────────────┐
        │         PHASE 1: LEXICAL ANALYSIS                  │
        │              (lexer.py)                            │
        │                                                    │
        │  • Reads source code character by character       │
        │  • Recognizes patterns (keywords, identifiers)    │
        │  • Creates tokens with types and values           │
        │  • Skips whitespace and comments                  │
        └────────────────────┬───────────────────────────────┘
                             │
                             │ Token Stream
                             │ [LOAD, STRING, FILTER, ...]
                             ▼
        ┌────────────────────────────────────────────────────┐
        │         PHASE 2: SYNTAX ANALYSIS                   │
        │              (parser.py)                           │
        │                                                    │
        │  • Validates grammar rules                        │
        │  • Builds Abstract Syntax Tree (AST)              │
        │  • Detects syntax errors                          │
        │  • Creates structured representation              │
        └────────────────────┬───────────────────────────────┘
                             │
                             │ Abstract Syntax Tree (AST)
                             │ [LoadNode, FilterNode, ...]
                             ▼
        ┌────────────────────────────────────────────────────┐
        │         PHASE 3: SEMANTIC ANALYSIS                 │
        │              (semantic.py)                         │
        │                                                    │
        │  • Validates logical correctness                  │
        │  • Checks file existence                          │
        │  • Verifies column names                          │
        │  • Ensures proper command sequence                │
        └────────────────────┬───────────────────────────────┘
                             │
                             │ Validated AST
                             │ (With error/warning report)
                             ▼
        ┌────────────────────────────────────────────────────┐
        │         PHASE 4: CODE GENERATION                   │
        │              (codegen.py)                          │
        │                                                    │
        │  • Traverses validated AST                        │
        │  • Generates Python/Pandas code                   │
        │  • Adds imports and comments                      │
        │  • Creates executable script                      │
        └────────────────────┬───────────────────────────────┘
                             │
                             │ Generated Python Code
                             ▼
                     ┌───────────────────┐
                     │  Python Script    │
                     │  (output.py)      │
                     └───────────────────┘
```

## Component Details

```
┌─────────────────────────────────────────────────────────────────────┐
│                          MAIN COMPILER                               │
│                           (main.py)                                  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  DTLCompiler Class                                        │     │
│  │  ├─ __init__(source_file, output_file)                   │     │
│  │  ├─ compile()          → Orchestrates all phases         │     │
│  │  ├─ _run_lexer()       → Phase 1                         │     │
│  │  ├─ _run_parser()      → Phase 2                         │     │
│  │  ├─ _run_semantic()    → Phase 3                         │     │
│  │  └─ _run_codegen()     → Phase 4                         │     │
│  └───────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                        LEXER (lexer.py)                              │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Lexer Class                                              │     │
│  │  ├─ tokenize()           → Main tokenization             │     │
│  │  ├─ _tokenize_line()     → Process single line           │     │
│  │  └─ Token recognition:                                    │     │
│  │     • Keywords (load, filter, select, ...)               │     │
│  │     • Identifiers (column names)                          │     │
│  │     • Operators (>, <, ==, ...)                           │     │
│  │     • Literals (strings, numbers)                         │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  TokenType Enum                                           │     │
│  │  • LOAD, FILTER, SELECT, SORT, SAVE, GROUP              │     │
│  │  • GT, LT, GTE, LTE, EQ, NEQ                             │     │
│  │  • STRING, NUMBER, IDENTIFIER                             │     │
│  │  • SUM, AVG, COUNT, MAX, MIN                             │     │
│  └───────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                     PARSER (parser.py)                               │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Parser Class                                             │     │
│  │  ├─ parse()              → Main parsing method           │     │
│  │  ├─ _parse_command()     → Route to specific parser      │     │
│  │  ├─ _parse_load()        → Load command                  │     │
│  │  ├─ _parse_filter()      → Filter command                │     │
│  │  ├─ _parse_select()      → Select command                │     │
│  │  ├─ _parse_sort()        → Sort command                  │     │
│  │  ├─ _parse_save()        → Save command                  │     │
│  │  └─ _parse_group()       → Group by command              │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  Helper Methods:                                                     │
│  • _peek()          → Look at current token                         │
│  • _advance()       → Move to next token                            │
│  • _consume()       → Expect specific token type                    │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                   AST NODES (ast_nodes.py)                           │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Abstract Syntax Tree Node Hierarchy                      │     │
│  │                                                            │     │
│  │           ASTNode (Base Class)                            │     │
│  │                  ▲                                         │     │
│  │                  │                                         │     │
│  │     ┌────────────┼────────────┐                          │     │
│  │     │            │            │                           │     │
│  │  LoadNode   FilterNode   SelectNode                       │     │
│  │     │            │            │                           │     │
│  │  SortNode   SaveNode   GroupByNode                        │     │
│  │                                                            │     │
│  │  Program (Root Node - contains all commands)              │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  Node Details:                                                       │
│  • LoadNode(filename)                                                │
│  • FilterNode(column, operator, value)                               │
│  • SelectNode(columns[])                                             │
│  • SortNode(column, order)                                           │
│  • SaveNode(filename)                                                │
│  • GroupByNode(column, agg_col, agg_func)                           │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│              SEMANTIC ANALYZER (semantic.py)                         │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  SemanticAnalyzer Class                                   │     │
│  │  ├─ analyze()              → Main analysis method        │     │
│  │  ├─ _analyze_command()     → Check single command        │     │
│  │  ├─ _analyze_load()        → Validate file exists        │     │
│  │  ├─ _analyze_filter()      → Check column exists         │     │
│  │  ├─ _analyze_select()      → Verify columns valid        │     │
│  │  ├─ _analyze_sort()        → Check sort column           │     │
│  │  ├─ _analyze_save()        → Validate output path        │     │
│  │  └─ _analyze_group()       → Check grouping valid        │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  Validation Checks:                                                  │
│  • File existence (input CSV)                                        │
│  • Column name validation                                            │
│  • Command sequence (load must be first)                             │
│  • Operator validity                                                 │
│  • Aggregate function validity                                       │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                 CODE GENERATOR (codegen.py)                          │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  CodeGenerator Class                                      │     │
│  │  ├─ generate()            → Main generation method       │     │
│  │  ├─ _generate_command()   → Route to specific generator  │     │
│  │  ├─ _generate_load()      → pd.read_csv(...)            │     │
│  │  ├─ _generate_filter()    → df[df[col] op val]          │     │
│  │  ├─ _generate_select()    → df[[cols]]                  │     │
│  │  ├─ _generate_sort()      → df.sort_values(...)         │     │
│  │  ├─ _generate_save()      → df.to_csv(...)              │     │
│  │  └─ _generate_group()     → df.groupby(...).agg(...)    │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  Output Format:                                                      │
│  • Imports (import pandas as pd)                                     │
│  • Comments (# Load data from ...)                                   │
│  • Pandas code (df = ...)                                            │
│  • Print statements (progress feedback)                              │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

```
Input DTL Script:
┌─────────────────────────────┐
│ load "employees.csv"        │
│ filter salary > 70000       │
│ select name, salary         │
│ sort by salary desc         │
│ save "output.csv"           │
└─────────────────────────────┘
           │
           ▼
    LEXER PHASE
┌─────────────────────────────┐
│ Token(LOAD, 'load')         │
│ Token(STRING, 'employees')  │
│ Token(FILTER, 'filter')     │
│ Token(IDENTIFIER, 'salary') │
│ Token(GT, '>')              │
│ Token(NUMBER, '70000')      │
│ ...                         │
└─────────────────────────────┘
           │
           ▼
    PARSER PHASE
┌─────────────────────────────┐
│ Program                     │
│  ├─ LoadNode(employees.csv) │
│  ├─ FilterNode(salary,>,70k)│
│  ├─ SelectNode([name,sal])  │
│  ├─ SortNode(salary,desc)   │
│  └─ SaveNode(output.csv)    │
└─────────────────────────────┘
           │
           ▼
  SEMANTIC PHASE
┌─────────────────────────────┐
│ File exists              │
│ Columns valid            │
│ Operators correct        │
│ Command sequence OK      │
└─────────────────────────────┘
           │
           ▼
   CODEGEN PHASE
┌─────────────────────────────┐
│ import pandas as pd         │
│                             │
│ df = pd.read_csv(...)       │
│ df = df[df["salary"]>70000] │
│ df = df[["name","salary"]]  │
│ df = df.sort_values(...)    │
│ df.to_csv("output.csv")     │
└─────────────────────────────┘
           │
           ▼
    Output Python Script
```

## Module Dependencies

```
                main.py
                   │
      ┌────────────┼────────────┐
      │            │            │
   lexer.py    parser.py    semantic.py
      │            │            │
      │        ast_nodes.py     │
      │            │            │
      └────────────┼────────────┘
                   │
              codegen.py
                   │
            ast_nodes.py
```

## File Size & Complexity

```
┌──────────────┬───────┬────────────┬─────────────┐
│ File         │ Lines │ Classes    │ Functions   │
├──────────────┼───────┼────────────┼─────────────┤
│ ast_nodes.py │   80  │ 8 classes  │ -           │
│ lexer.py     │  200  │ 2 classes  │ 1 function  │
│ parser.py    │  250  │ 1 class    │ 1 function  │
│ semantic.py  │  200  │ 1 class    │ -           │
│ codegen.py   │  180  │ 1 class    │ -           │
│ main.py      │  200  │ 1 class    │ 1 function  │
├──────────────┼───────┼────────────┼─────────────┤
│ TOTAL        │ 1110  │ 14 classes │ 3 functions │
└──────────────┴───────┴────────────┴─────────────┘
```

## Compilation Pipeline Timing

```
┌────────────────────────────────────────────────┐
│ Typical Compilation (example1.dtl)            │
├────────────────────────────────────────────────┤
│ Phase 1: Lexical Analysis      ~0.01 seconds   │
│ Phase 2: Syntax Analysis        ~0.02 seconds  │
│ Phase 3: Semantic Analysis      ~0.05 seconds  │
│ Phase 4: Code Generation        ~0.01 seconds  │
├────────────────────────────────────────────────┤
│ Total Compilation Time:         ~0.09 seconds  │
└────────────────────────────────────────────────┘

Execution Time: ~0.05 seconds (for 15 row CSV)
```

## Error Handling Flow

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ LEXER           │──► Unknown character → SyntaxError
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ PARSER          │──► Invalid syntax → SyntaxError
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ SEMANTIC        │──► Missing file → SemanticError
│                 │──► Invalid column → SemanticError
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ CODE GENERATOR  │──► (No errors at this stage)
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Success!     │
└─────────────────┘
```

---

**End of Architecture Diagram**

For more details, see DOCUMENTATION.md