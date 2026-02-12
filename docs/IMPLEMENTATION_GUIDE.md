# DTL Compiler - Step-by-Step Implementation Guide

## Day 1: Planning & Design (2-3 hours)

### Tasks
1. **Understand the Requirements**
   - Read through the project objectives
   - Study compiler phases
   - Review example data transformations

2. **Design the DSL**
   - Define command syntax
   - Create grammar rules
   - Write example scripts

3. **Plan the Architecture**
   - Sketch the compiler phases
   - Identify modules needed
   - Define data structures

### Deliverables
- [ ] DSL specification document
- [ ] Example `.dtl` scripts (3-5 examples)
- [ ] Architecture diagram (hand-drawn or digital)

### Tips
- Keep the language simple - you can extend it later
- Focus on core commands: load, filter, select, sort, save
- Test your examples mentally to ensure they make sense

---

## Day 2: Lexer Implementation (3-4 hours)

### Tasks
1. **Create `ast_nodes.py`**
   - Define base `ASTNode` class
   - Create node classes for each command
   - Add `__repr__` methods for debugging

2. **Implement `lexer.py`**
   - Define `TokenType` enum
   - Create `Token` class
   - Implement `Lexer` class with tokenization logic
   - Add pattern matching for strings, numbers, identifiers

3. **Test the Lexer**
   - Write test cases
   - Verify token generation
   - Handle edge cases

### Code to Write
```python
# ast_nodes.py (~80 lines)
- ASTNode base class
- LoadNode, FilterNode, SelectNode, SortNode, SaveNode, GroupByNode
- Program class to hold commands

# lexer.py (~200 lines)
- TokenType enum (all token types)
- Token class
- Lexer class with tokenize() method
- Pattern matching logic
```

### Testing
```python
python lexer.py  # Run standalone test
```

### Common Issues & Solutions
- **Issue**: Strings not recognized
  - **Fix**: Check quote matching in regex
- **Issue**: Numbers with decimals fail
  - **Fix**: Update number regex to include `\.`

---

## Day 3: Parser Implementation (4-5 hours)

### Tasks
1. **Create `parser.py`**
   - Implement `Parser` class
   - Write parsing methods for each command
   - Add helper methods (peek, consume, advance)
   - Build AST from tokens

2. **Grammar Implementation**
   - `_parse_load()`: Load command
   - `_parse_filter()`: Filter with operators
   - `_parse_select()`: Comma-separated columns
   - `_parse_sort()`: Sort with optional asc/desc
   - `_parse_save()`: Save command
   - `_parse_group()`: Group by with aggregation

3. **Error Handling**
   - Add syntax error messages
   - Include line numbers in errors
   - Provide helpful suggestions

### Code to Write
```python
# parser.py (~250 lines)
- Parser class
- parse() main method
- Command parsing methods (_parse_load, _parse_filter, etc.)
- Helper methods (_peek, _consume, _advance)
- Error handling
```

### Testing
```python
python parser.py  # Run standalone test
```

### Common Issues & Solutions
- **Issue**: "Unexpected token" errors
  - **Fix**: Check token type matching in consume()
- **Issue**: AST nodes not created
  - **Fix**: Ensure all paths return a node

---

## Day 4: Semantic Analysis (3-4 hours)

### Tasks
1. **Create `semantic.py`**
   - Implement `SemanticAnalyzer` class
   - Add validation logic for each command type
   - Check file existence
   - Validate column names (optional)
   - Ensure proper command sequence

2. **Implement Validation Rules**
   - Program must start with `load`
   - Filter/select/sort require prior load
   - Column names must exist
   - Operators must be valid

3. **Error Reporting**
   - Collect errors and warnings
   - Create readable error messages
   - Add suggestions for fixing errors

### Code to Write
```python
# semantic.py (~200 lines)
- SemanticAnalyzer class
- analyze() method
- Command validation methods
- Error collection and reporting
```

### Testing
```python
python semantic.py  # Run standalone test
```

### Common Issues & Solutions
- **Issue**: False positive errors
  - **Fix**: Make file/column validation optional
- **Issue**: Missing warnings
  - **Fix**: Add warning collection alongside errors

---

## Day 5: Code Generation (4-5 hours)

### Tasks
1. **Create `codegen.py`**
   - Implement `CodeGenerator` class
   - Write code generation for each command
   - Use f-strings for template-based generation
   - Add comments to generated code

2. **Implement Generation Methods**
   - `_generate_load()`: Pandas read_csv
   - `_generate_filter()`: Boolean indexing
   - `_generate_select()`: Column selection
   - `_generate_sort()`: sort_values
   - `_generate_save()`: to_csv
   - `_generate_group()`: groupby with aggregation

3. **Add Quality Features**
   - Import statements at top
   - Helpful comments in generated code
   - Print statements for user feedback
   - Proper formatting (indentation, spacing)

### Code to Write
```python
# codegen.py (~180 lines)
- CodeGenerator class
- generate() main method
- Command generation methods
- save_to_file() method
```

### Testing
```python
python codegen.py  # Run standalone test
# Then test the generated output.py
python generated_output.py
```

### Common Issues & Solutions
- **Issue**: Generated code has syntax errors
  - **Fix**: Check string escaping and quotes
- **Issue**: Pandas functions incorrect
  - **Fix**: Map DSL functions to Pandas equivalents (avg → mean)

---

## Day 6: Integration & Testing (4-5 hours)

### Tasks
1. **Create `main.py`**
   - Implement `DTLCompiler` class
   - Coordinate all compilation phases
   - Add command-line interface
   - Implement option parsing

2. **Integration Testing**
   - Test with example1.dtl (basic filtering)
   - Test with example2.dtl (complex filters)
   - Test with example3.dtl (grouping)
   - Test error cases

3. **Bug Fixing**
   - Fix any integration issues
   - Improve error messages
   - Handle edge cases

4. **Create Test Data**
   - Generate sample CSV files
   - Create diverse test scenarios
   - Verify outputs are correct

### Code to Write
```python
# main.py (~200 lines)
- DTLCompiler class
- compile() method orchestrating all phases
- Command-line argument parsing
- User-friendly output formatting
```

### Testing Checklist
- [ ] All example scripts compile successfully
- [ ] Generated Python code runs without errors
- [ ] Output CSV files contain correct data
- [ ] Error messages are clear and helpful
- [ ] All command-line options work

### Common Issues & Solutions
- **Issue**: Compilation fails silently
  - **Fix**: Add try-catch blocks with detailed error messages
- **Issue**: Generated code doesn't run
  - **Fix**: Test each phase separately to isolate the problem

---

## Day 7: Documentation & Submission (3-4 hours)

### Tasks
1. **Write Documentation**
   - Create comprehensive README.md
   - Write DOCUMENTATION.md with technical details
   - Add inline code comments
   - Document all functions and classes

2. **Prepare Examples**
   - Ensure all example scripts work
   - Create variety of test cases
   - Include both simple and complex examples

3. **Final Testing**
   - Run all examples one more time
   - Verify generated code quality
   - Check for any remaining bugs

4. **Organize Deliverables**
   - Organize files in proper structure
   - Create zip file if needed
   - Prepare for submission

### Documentation Checklist
- [ ] README.md with usage instructions
- [ ] DOCUMENTATION.md with technical details
- [ ] Inline comments in all source files
- [ ] Example scripts with comments
- [ ] Project report (if required)

### Submission Checklist
- [ ] All source files (.py)
- [ ] All example scripts (.dtl)
- [ ] Test data (CSV files)
- [ ] Documentation (README, DOCUMENTATION)
- [ ] Generated examples (output.py files)
- [ ] Architecture diagram

---

## Quick Start Commands

### Setup
```bash
# Create project structure
mkdir DTL_Compiler
cd DTL_Compiler
mkdir test_data

# Install dependencies
pip install pandas
```

### Development Workflow
```bash
# Day 2: Test lexer
python lexer.py

# Day 3: Test parser
python parser.py

# Day 4: Test semantic analyzer
python semantic.py

# Day 5: Test code generator
python codegen.py

# Day 6+: Full compilation
python main.py example1.dtl
python generated_output.py
```

---

## Pro Tips for Success

### Time Management
- **Don't perfectionist** - Get it working first, polish later
- **Test incrementally** - Test each component before moving on
- **Keep scope small** - Focus on core features, extensions are optional

### Debugging Strategies
1. **Print statements** - Add debug prints in each phase
2. **Test small inputs** - Start with 1-2 line scripts
3. **Isolate issues** - Test each module independently
4. **Read error messages** - Pandas errors often suggest the fix

### Code Quality
- **Use meaningful names** - `parse_filter()` not `pf()`
- **Add comments** - Explain the "why", not the "what"
- **Consistent style** - Use same naming convention throughout
- **Error messages matter** - Users will appreciate clear errors

### Presentation Tips
- **Show the architecture diagram** - Demonstrates understanding
- **Live demo** - Compile and run an example script
- **Explain trade-offs** - Why you chose this approach
- **Discuss extensions** - Show you're thinking beyond the assignment

---

## 📊 Estimated Time Breakdown

| Day | Phase | Hours | Complexity |
|-----|-------|-------|------------|
| 1   | Planning & Design | 2-3 | Easy |
| 2   | Lexer | 3-4 | Medium |
| 3   | Parser | 4-5 | Hard |
| 4   | Semantic | 3-4 | Medium |
| 5   | Code Gen | 4-5 | Medium |
| 6   | Integration & Testing | 4-5 | Medium |
| 7   | Documentation | 3-4 | Easy |
| **Total** | | **23-30 hours** | |

---

## Definition of Done

Your project is complete when:
- [ ] All source files are implemented and tested
- [ ] At least 3 example scripts compile and run successfully
- [ ] Generated Python code executes without errors
- [ ] Documentation is comprehensive and clear
- [ ] Error handling provides helpful feedback
- [ ] Code is well-commented and organized
- [ ] You can explain each compiler phase confidently

---

## Minimum Viable Product (MVP)

If short on time, focus on:
1. Load command
2. Filter command (numeric comparison only)
3. Select command
4. Save command
5. Basic error handling

This demonstrates all compiler phases with minimal features.

---

## Extensions (If Time Allows)

1. **Add GROUP BY** - Already implemented!
2. **Support multiple operators** - AND/OR in filters
3. **Add JOIN** - Merge datasets
4. **Expression evaluation** - Computed columns
5. **Better error recovery** - Continue after errors
6. **Optimization** - Remove redundant operations
7. **REPL mode** - Interactive testing

---

## Resources

### Python Libraries
- **pandas**: Data manipulation
- **re**: Regular expressions for tokenization

### Concepts to Review
- Finite Automata (for lexer)
- Context-Free Grammars (for parser)
- Tree traversal (for code generation)
- Symbol tables (for semantic analysis)

### Helpful Examples
- Look at Python's own parser (ast module)
- Study simple expression evaluators
- Read about recursive descent parsing

---

**Good luck with your project! 🚀**

Remember: The goal is to demonstrate understanding of compiler concepts, not to build a production-ready system. Keep it simple, test frequently, and document well!