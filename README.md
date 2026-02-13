# DTL Compiler - Data Transformation Language Compiler

A Domain-Specific Language (DSL) Compiler for Data Transformation

## Project Overview

This is a complete compiler implementation that translates Data Transformation Language (DTL) scripts into executable Python code using Pandas. It demonstrates all major phases of compiler design:

1. Lexical Analysis (Tokenization)
2. Syntax Analysis (Parsing)
3. Semantic Analysis (Validation)
4. Code Generation (Python/Pandas output)

## Features

- Custom domain-specific language for data operations
- Complete lexer with regex-based tokenization
- Recursive descent parser with AST construction
- Semantic validation (file existence, column checks)
- Python/Pandas code generation
- Command-line interface
- Comprehensive error reporting
- Support for filtering, selecting, sorting, grouping, and aggregation

## Project Structure

```
DTL_Compiler/
│
├── src/
│   ├── main.py              # Main compiler driver
│   ├── lexer.py             # Lexical analyzer (tokenizer)
│   ├── parser.py            # Syntax analyzer (parser)
│   ├── ast_nodes.py         # AST node definitions
│   ├── semantic.py          # Semantic analyzer
│   └── codegen.py           # Code generator
│
├── examples/
│   ├── example1.dtl         # Sample DTL script 1
│   ├── example2.dtl         # Sample DTL script 2
│   └── example3.dtl         # Sample DTL script 3
│
├── test_data/
│   └── employees.csv        # Sample dataset
│
├── docs/
│   ├── ARCHITECTURE.md      # Architecture documentation
│   └── README.md            # Additional docs
│
├── web/
│   └── app.py               # Web interface
│
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pandas library

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Compiler

Basic usage:
```bash
python src/main.py examples/example1.dtl
```

With options:
```bash
python src/main.py examples/example1.dtl --output outputs/my_script.py --verbose
```

Run the generated code:
```bash
python outputs/generated_output.py
```

## DTL Language Syntax

### Supported Commands

1. LOAD - Load data from CSV file
   ```
   load "filename.csv"
   ```

2. FILTER - Filter rows based on conditions
   ```
   filter column_name > value
   ```

3. SELECT - Select specific columns
   ```
   select column1, column2, column3
   ```

4. SORT - Sort data by column
   ```
   sort by column_name asc
   ```

5. GROUP BY - Group and aggregate data
   ```
   group by column aggregate_function target_column
   ```

6. SAVE - Save results to CSV file
   ```
   save "output.csv"
   ```

### Example DTL Script

```dtl
load "test_data/employees.csv"
filter salary > 70000
select name, department, salary
sort by salary desc
save "outputs/high_earners.csv"
```

## License

This is an academic project for educational purposes.

## Author

Computer Science Student - Compiler Design Project 2026

#### 4. **SORT** - Sort data by column
```
sort by column_name asc
sort by salary desc
```

Orders: `asc` (ascending), `desc` (descending)

#### 5. **GROUP BY** - Group and aggregate data
```
group by column aggregate_function target_column
group by department avg salary
group by category sum revenue
```

Aggregate functions: `sum`, `avg`, `count`, `max`, `min`

#### 6. **SAVE** - Save results to CSV file
```
save "output.csv"
```

### Example DTL Script

```dtl
load "test_data/employees.csv"
filter salary > 70000
select name, department, salary
sort by salary desc
save "outputs/high_earners.csv"
```

## License

This is an academic project for educational purposes.

## Author

Computer Science Student - Compiler Design Project 2026