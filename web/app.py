"""
DTL Compiler - Flask Web Interface
Complete rewrite with proper error handling and semantic validation
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import re
import subprocess
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from codegen import CodeGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvfile' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['csvfile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Invalid file type. Please upload a CSV.'}), 400
    
    filename = 'uploaded_data.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        df = pd.read_csv(filepath, on_bad_lines='skip', engine='python', nrows=50)
        preview = {
            'columns': df.columns.tolist(),
            'rows': df.head(10).replace({float('nan'): 'NaN'}).to_dict('records'),
            'total_rows': len(df)
        }
        return jsonify({'success': True, 'filename': filename, 'preview': preview})
    except Exception as e:
        return jsonify({'error': f'Error reading CSV preview: {str(e)}'}), 400


@app.route('/compile', methods=['POST'])
def compile_dtl():
    data = request.json
    dtl_code = data.get('dtl_code', '')
    target_filename = data.get('filename', '') 
    
    if not dtl_code:
        return jsonify({'error': 'No DTL code provided'}), 400

    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        if f.endswith('.csv') or f == 'generated_output.py':
            try:
                os.remove(os.path.join(app.config['OUTPUT_FOLDER'], f))
            except:
                pass
    
    try:
        if target_filename:
            server_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], target_filename))
            normalized_path = server_path.replace("\\", "/")
            dtl_code = re.sub(r'load\s+"[^"]+"', f'load "{normalized_path}"', dtl_code)
        
        def _save_replace(m):
            orig_name = os.path.basename(m.group(1))
            full_out_path = os.path.abspath(os.path.join(app.config['OUTPUT_FOLDER'], orig_name))
            return f'save "{full_out_path.replace("\\", "/")}"'
        
        dtl_code = re.sub(r'save\s+"([^"]+)"', _save_replace, dtl_code)

        lexer = Lexer(dtl_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer(ast, validate_files=True, validate_columns=True)
        if not analyzer.analyze():
            error_msg = f"Semantic validation failed ({len(analyzer.errors)} errors):\n"
            error_msg += "\n".join([f"  • {e}" for e in analyzer.errors])
            
            if analyzer.warnings:
                error_msg += f"\n\nWarnings ({len(analyzer.warnings)}):\n"
                error_msg += "\n".join([f"  • {w}" for w in analyzer.warnings])
            
            return jsonify({'error': error_msg}), 400
        
        codegen = CodeGenerator(ast)
        python_code = codegen.generate()
        
        output_py = os.path.join(app.config['OUTPUT_FOLDER'], 'generated_output.py')
        with open(output_py, 'w') as f:
            f.write(python_code)
        
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['python', output_py], 
            capture_output=True, 
            text=True, 
            cwd=repo_root,
            timeout=30
        )
        
        output_data = None
        csv_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.endswith('.csv')]
        
        if csv_files:
            csv_file = csv_files[0]
            try:
                out_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_file)
                out_df = pd.read_csv(out_path)
                output_data = {
                    'columns': out_df.columns.tolist(),
                    'rows': out_df.head(20).replace({float('nan'): 'NaN'}).to_dict('records'),
                    'total_rows': len(out_df),
                    'filename': csv_file
                }
            except Exception as e:
                return jsonify({'error': f'Error reading output CSV: {str(e)}'}), 500
        else:
            if result.returncode != 0:
                return jsonify({'error': f'Script execution failed:\n{result.stderr}'}), 500
        
        response_data = {
            'success': True,
            'python_code': python_code,
            'execution_output': result.stdout,
            'output_data': output_data
        }
        
        if analyzer.warnings:
            response_data['warnings'] = analyzer.warnings
        
        return jsonify(response_data)
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script execution timed out (>30 seconds)'}), 500
    except Exception as e:
        import traceback
        return jsonify({'error': f'Compiler Exception: {str(e)}\n{traceback.format_exc()}'}), 500


@app.route('/download/<file_type>')
def download_file(file_type):
    folder = app.config['OUTPUT_FOLDER']
    
    if file_type == 'python':
        path = os.path.join(folder, 'generated_output.py')
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name='generated_output.py')
        return jsonify({'error': 'Python script not found'}), 404
        
    elif file_type == 'csv':
        csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
        if csv_files:
            csv_path = os.path.join(folder, csv_files[0])
            return send_file(csv_path, as_attachment=True, download_name=csv_files[0])
        return jsonify({'error': 'No CSV output file found'}), 404
    
    return jsonify({'error': 'Invalid file type'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)