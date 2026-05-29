#!/usr/bin/env python3
"""
Web Interface for Text2SQL RAG System
Simple Flask web application for easy access
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from text2sql_rag.ultimate_prompt import UltimatePromptBuilder
    from text2sql_rag.llm import call_llm, extract_sql
    from text2sql_rag.validator import SQLValidator
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the src directory is properly set up")

app = Flask(__name__)

# Initialize components
try:
    prompt_builder = UltimatePromptBuilder()
    validator = SQLValidator()
    print("Text2SQL RAG System loaded successfully")
except Exception as e:
    print(f"Error initializing system: {e}")
    prompt_builder = None
    validator = None

@app.route('/')
def index():
    """Main page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Text2SQL RAG System</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
            .error { border-left-color: #dc3545; background: #f8d7da; }
            .success { border-left-color: #28a745; background: #d4edda; }
            .sql-output { background: #f1f1f1; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
            .loading { display: none; text-align: center; }
            .examples { margin: 20px 0; }
            .example { display: inline-block; margin: 5px; padding: 5px 10px; background: #e9ecef; border-radius: 3px; cursor: pointer; font-size: 12px; }
            .example:hover { background: #007bff; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Text2SQL RAG System</h1>
            <p style="text-align: center; color: #666;">Convert Thai questions to SQL queries using AI</p>
            
            <form id="sqlForm">
                <div class="form-group">
                    <label for="question">Question (Thai):</label>
                    <textarea id="question" name="question" rows="3" placeholder="Example: แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล"></textarea>
                </div>
                
                <div class="examples">
                    <strong>Examples:</strong><br>
                    <span class="example" onclick="setExample('แสดงชื่อผู้ป่วยทั้งหมด')">แสดงชื่อผู้ป่วยทั้งหมด</span>
                    <span class="example" onclick="setExample('จำนวนผู้ป่วยแต่ละโรงพยาบาล')">จำนวนผู้ป่วยแต่ละโรงพยาบาล</span>
                    <span class="example" onclick="setExample('ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค')">ค่าใช้จ่ายเฉลี่ยของผู้ป่วยแต่ละโรค</span>
                    <span class="example" onclick="setExample('ผู้ป่วยที่มีอายุมากกว่า 50 ปี')">ผู้ป่วยที่มีอายุมากกว่า 50 ปี</span>
                </div>
                
                <div class="form-group">
                    <label for="llm_model">LLM Model:</label>
                    <select id="llm_model" name="llm_model">
                        <option value="typhoon">Typhoon (Thai)</option>
                        <option value="openai">OpenAI GPT</option>
                        <option value="claude">Anthropic Claude</option>
                    </select>
                </div>
                
                <button type="submit">Generate SQL</button>
            </form>
            
            <div class="loading" id="loading">
                <p>Generating SQL... Please wait.</p>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            function setExample(question) {
                document.getElementById('question').value = question;
            }
            
            document.getElementById('sqlForm').onsubmit = function(e) {
                e.preventDefault();
                
                const question = document.getElementById('question').value;
                const llm_model = document.getElementById('llm_model').value;
                
                if (!question.trim()) {
                    alert('Please enter a question');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').innerHTML = '';
                
                fetch('/generate_sql', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: question,
                        llm_model: llm_model
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    displayResult(data);
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').innerHTML = 
                        '<div class="result error"><strong>Error:</strong> ' + error + '</div>';
                });
            };
            
            function displayResult(data) {
                let html = '';
                
                if (data.status === 'success') {
                    html += '<div class="result success">';
                    html += '<h3>Generated SQL:</h3>';
                    html += '<div class="sql-output">' + data.generated_sql + '</div>';
                    html += '<p><strong>Question Type:</strong> ' + data.question_type + '</p>';
                    html += '<p><strong>Processing Time:</strong> ' + data.latency.toFixed(3) + 's</p>';
                    
                    if (data.validation && data.validation.warnings.length > 0) {
                        html += '<p><strong>Warnings:</strong></p><ul>';
                        data.validation.warnings.forEach(warning => {
                            html += '<li>' + warning + '</li>';
                        });
                        html += '</ul>';
                    }
                    
                    html += '</div>';
                } else {
                    html += '<div class="result error">';
                    html += '<h3>Error:</h3>';
                    html += '<p>' + data.error + '</p>';
                    html += '</div>';
                }
                
                document.getElementById('result').innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/generate_sql', methods=['POST'])
def generate_sql():
    """Generate SQL from question"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        llm_model = data.get('llm_model', 'typhoon')
        
        if not question:
            return jsonify({'status': 'error', 'error': 'No question provided'})
        
        if not prompt_builder:
            return jsonify({'status': 'error', 'error': 'System not initialized'})
        
        start_time = datetime.now()
        
        # Default schema
        schema = """- Name (TEXT): Patient name
- Age (INTEGER): Patient age
- Hospital (TEXT): Hospital name
- Medical_Condition (TEXT): Medical condition
- "Billing Amount" (REAL): Billing amount
- DoctorID (INTEGER): Doctor ID"""
        
        # Build prompt
        prompt = prompt_builder.build_ultimate_prompt(question, schema)
        
        # Analyze question type
        question_type = prompt_builder._analyze_question_type(question)
        
        # Generate SQL (with error handling for missing API keys)
        try:
            llm_response = call_llm(llm_model, prompt)
            generated_sql = extract_sql(llm_response)
        except Exception as e:
            # Fallback to mock response for demo
            generated_sql = "-- Mock SQL (API not available)\nSELECT p.Name FROM patients p;"
        
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds()
        
        # Validate SQL
        validation_result = None
        if validator:
            validation_result = validator.validate_sql(generated_sql)
        
        return jsonify({
            'status': 'success',
            'question': question,
            'question_type': question_type,
            'generated_sql': generated_sql,
            'latency': latency,
            'prompt_length': len(prompt),
            'validation': {
                'is_valid': validation_result.is_valid if validation_result else True,
                'errors': validation_result.errors if validation_result else [],
                'warnings': validation_result.warnings if validation_result else [],
                'suggestions': validation_result.suggestions if validation_result else []
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system_initialized': prompt_builder is not None,
        'validator_available': validator is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Text2SQL RAG Web Interface...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)


