# DTL Compiler - Data Transformation Language Compiler

**A Domain-Specific Language (DSL) Compiler for Data Transformation**

## 📋 Project Overview

This is a complete compiler implementation that translates Data Transformation Language (DTL) scripts into executable Python code using Pandas. It demonstrates all major phases of compiler design:

1. **Lexical Analysis** (Tokenization)
2. **Syntax Analysis** (Parsing)
3. **Semantic Analysis** (Validation)
4. **Code Generation** (Python/Pandas output)

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
├── main.py              # Main compiler driver
├── lexer.py             # Lexical analyzer (tokenizer)
├── parser.py            # Syntax analyzer (parser)
├── ast_nodes.py         # AST node definitions
├── semantic.py          # Semantic analyzer
├── codegen.py           # Code generator
│
├── example1.dtl         # Sample DTL script 1
├── example2.dtl         # Sample DTL script 2
├── example3.dtl         # Sample DTL script 3
│
├── test_data/
│   └── employees.csv    # Sample dataset
│
├── README.md            # This file
└── DOCUMENTATION.md     # Complete project documentation
```

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pandas library

Install pandas:
```bash
pip install pandas
```

### Running the Compiler

**Basic usage:**
```bash
python main.py example1.dtl
```

**With options:**
```bash
python main.py example1.dtl --output my_script.py --verbose
```

**Run the generated code:**
```bash
python generated_output.py
```

## DTL Language Syntax

### Supported Commands

#### 1. **LOAD** - Load data from CSV file
```
load "filename.csv"
```

#### 2. **FILTER** - Filter rows based on conditions
```
filter column_name > value
filter age >= 25
filter department == Engineering
filter salary != 50000
```

Supported operators: `>`, `<`, `>=`, `<=`, `==`, `!=`

#### 3. **SELECT** - Select specific columns
```
select column1, column2, column3
select name, age, salary
```

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
# Filter high-earning employees
load "test_data/employees.csv"
filter salary > 70000
select name, department, salary
sort by salary desc
save "test_data/high_earners.csv"
```

### Generated Python Code

```python
import pandas as pd

# Load data from test_data/employees.csv
df = pd.read_csv("test_data/employees.csv")
print(f"Loaded {len(df)} rows from test_data/employees.csv")

# Filter: salary > 70000
df = df[df["salary"] > 70000]
print(f"After filter: {len(df)} rows remaining")

# Select columns: name, department, salary
df = df[["name", "department", "salary"]]
print(f"Selected 3 columns")

# Sort by salary (desc)
df = df.sort_values(by="salary", ascending=False)
print(f"Sorted by salary (desc)")

# Save results to test_data/high_earners.csv
df.to_csv("test_data/high_earners.csv", index=False)
print(f"Saved {len(df)} rows to test_data/high_earners.csv")

print("Data transformation completed successfully!")
```

## 🧪 Testing the Compiler

### Test Example 1
```bash
python main.py example1.dtl
python generated_output.py
```

### Test Example 2
```bash
python main.py example2.dtl --output example2_output.py
python example2_output.py
```

### Test Example 3 (with grouping)
```bash
python main.py example3.dtl --verbose
python generated_output.py
```

## Compiler Architecture

```
┌─────────────────────┐
│   DTL Source Code   │
│    (.dtl file)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LEXER (lexer.py)  │
│   Tokenization      │
└──────────┬──────────┘
           │ Tokens
           ▼
┌─────────────────────┐
│  PARSER (parser.py) │
│   Syntax Analysis   │
└──────────┬──────────┘
           │ AST
           ▼
┌─────────────────────┐
│ SEMANTIC ANALYZER   │
│   (semantic.py)     │
└──────────┬──────────┘
           │ Validated AST
           ▼
┌─────────────────────┐
│ CODE GENERATOR      │
│   (codegen.py)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python/Pandas Code │
│   (executable)      │
└─────────────────────┘
```

## Command-Line Options

```
python main.py <input_file.dtl> [options]

Options:
  --output <file>         Specify output file (default: generated_output.py)
  --no-file-check         Skip file existence validation
  --validate-columns      Enable column validation (requires actual CSV)
  --verbose               Show detailed compilation steps
  --show-code             Display generated code

Examples:
  python main.py example1.dtl
  python main.py example1.dtl --output my_script.py --verbose
  python main.py example2.dtl --show-code
```

## 📊 Example Outputs

### High Salary Employees (example1.dtl)
Creates a filtered list of employees earning over $70,000, sorted by salary.

### Young Engineers (example2.dtl)
Filters engineering department employees under 35 with at least 2 years experience.

### Department Salary Analysis (example3.dtl)
Groups employees by department and calculates average salary per department.

## 🛠️ Development

### Running Individual Components

**Test Lexer:**
```bash
python lexer.py
```

**Test Parser:**
```bash
python parser.py
```

**Test Code Generator:**
```bash
python codegen.py
```

### Creating Your Own DTL Scripts

1. Create a new `.dtl` file
2. Write your transformation commands
3. Compile: `python main.py yourscript.dtl`
4. Run: `python generated_output.py`

## Learning Outcomes

This project demonstrates:

- **Lexical Analysis**: Pattern matching, tokenization, regex
- **Syntax Analysis**: Grammar rules, parsing, AST construction
- **Semantic Analysis**: Type checking, symbol tables, error detection
- **Code Generation**: Template-based code emission
- **Compiler Design**: Multi-phase architecture, separation of concerns
- **Domain-Specific Languages**: Custom language design
- **Source-to-Source Translation**: Transpiler concepts

## Project Grading Rubric Coverage

| Component | Implementation | Points |
|-----------|---------------|---------|
| Lexer (Tokenization) | Complete with regex | 20% |
| Parser (Syntax Analysis) | Recursive descent + AST | 25% |
| Semantic Analysis | Validation logic | 20% |
| Code Generation | Pandas code output | 25% |
| Documentation | Complete README + docs | 10% |

## Extensions & Future Work

Potential enhancements:
- [ ] JOIN operations between datasets
- [ ] More aggregate functions (median, mode)
- [ ] Support for Excel files
- [ ] Interactive REPL mode
- [ ] Optimization of generated code
- [ ] Better error messages with line numbers
- [ ] Support for expressions in filters
- [ ] Variables and computed columns

## License

This is an academic project for educational purposes.

## 👨‍💻 Author

Computer Science Student - Compiler Design Project 2025

## 📞 Support

For questions or issues:
1. Check DOCUMENTATION.md for detailed explanations
2. Review example scripts in the repository
3. Run with `--verbose` flag for debugging

---

**Happy Compiling! 🎉**