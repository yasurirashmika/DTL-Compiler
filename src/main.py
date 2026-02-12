"""
DTL Compiler - Main Driver
Coordinates all compiler phases: Lexer → Parser → Semantic → CodeGen
Updated to handle robust compilation for messy data.
"""

import sys
import os
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from codegen import CodeGenerator


class DTLCompiler:
    """Main compiler class that orchestrates the 4-phase pipeline"""
    
    def __init__(self, source_file, output_file=None, validate_files=True, validate_columns=False):
        self.source_file = source_file
        self.output_file = output_file or "generated_output.py"
        self.validate_files = validate_files
        self.validate_columns = validate_columns
        
        self.tokens = None
        self.ast = None
        self.generated_code = None
    
    def compile(self):
        """Execute all compilation phases in order"""
        print("=" * 60)
        print("DTL COMPILER - Data Transformation Language (Version 2.0)")
        print("=" * 60)
        
        try:
            # Phase 1: Lexical Analysis (Now supports NaN and specific data types)
            print("\n[Phase 1] Lexical Analysis...")
            self._run_lexer()
            print(f"Tokenization complete: {len(self.tokens)} tokens generated")
            
            # Phase 2: Syntax Analysis (Builds AST for cleaning and manipulation)
            print("\n[Phase 2] Syntax Analysis...")
            self._run_parser()
            print(f"Parsing complete: {len(self.ast.commands)} commands in AST")
            
            # Phase 3: Semantic Analysis (Validates column existence and logic)
            print("\n[Phase 3] Semantic Analysis...")
            is_valid = self._run_semantic_analysis()
            if not is_valid:
                print("\nCompilation failed due to semantic errors.")
                return False
            print("Semantic analysis passed.")
            
            # Phase 4: Code Generation (Generates robust Pandas code)
            print("\n[Phase 4] Code Generation...")
            self._run_code_generation()
            print(f"Code generation complete.")
            
            print("\n" + "=" * 60)
            print("COMPILATION SUCCESSFUL!")
            print("=" * 60)
            print(f"Generated file: {self.output_file}")
            print(f"Run it with: python {self.output_file}")
            
            return True
            
        except Exception as e:
            # Enhanced error reporting for debugging student projects
            print(f"\nCOMPILATION ERROR: {str(e)}")
            if '--verbose' in sys.argv:
                import traceback
                traceback.print_exc()
            return False
    
    def _run_lexer(self):
        with open(self.source_file, 'r') as f:
            source_code = f.read()
        
        lexer = Lexer(source_code)
        self.tokens = lexer.tokenize()
        
        if '--verbose' in sys.argv:
            lexer.print_tokens()
    
    def _run_parser(self):
        parser = Parser(self.tokens)
        self.ast = parser.parse()
        
        if '--verbose' in sys.argv:
            print("\n=== Abstract Syntax Tree ===")
            for i, command in enumerate(self.ast.commands, 1):
                print(f"{i}. {command}")
    
    def _run_semantic_analysis(self):
        # Uses the improved analyzer that handles messy CSV headers robustly
        analyzer = SemanticAnalyzer(
            self.ast, 
            validate_files=self.validate_files,
            validate_columns=self.validate_columns
        )
        is_valid = analyzer.analyze()
        analyzer.print_report()
        return is_valid
    
    def _run_code_generation(self):
        # Generates code with on_bad_lines='skip' to prevent CParserErrors
        codegen = CodeGenerator(self.ast)
        self.generated_code = codegen.save_to_file(self.output_file)
        
        if '--verbose' in sys.argv or '--show-code' in sys.argv:
            print("\n=== GENERATED PYTHON CODE ===")
            print(self.generated_code)


def main():
    """Command-line interface for the DTL Compiler"""
    print("""
╔════════════════════════════════════════════════════════════╗
║         DTL Compiler - Data Transformation Language        ║
║         Built for: University of Ruhuna Thesis             ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file.dtl> [options]")
        print("\nOptions:")
        print("  --output <file>     Specify output file (default: generated_output.py)")
        print("  --no-file-check     Skip file existence validation")
        print("  --validate-columns  Enable column validation (requires actual CSV)")
        print("  --verbose           Show detailed compilation steps")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Defaults and user-overrides
    output_file = "generated_output.py"
    validate_files = True
    validate_columns = False
    
    # Process Command Line Arguments
    for i in range(len(sys.argv)):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        elif sys.argv[i] == '--no-file-check':
            validate_files = False
        elif sys.argv[i] == '--validate-columns':
            validate_columns = True
    
    compiler = DTLCompiler(
        input_file, 
        output_file,
        validate_files=validate_files,
        validate_columns=validate_columns
    )
    
    success = compiler.compile()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()