#!/usr/bin/env python3
"""
DeadOPT - Main Optimizer Entry Point
Routes optimization requests to language-specific optimizers
"""

import sys
import json
import os

def main():
    if len(sys.argv) < 3:
        error_result = {
            "error": "Usage: python main_optimizer.py <language> <file_path>",
            "optimizedCode": "",
            "linesRemoved": 0,
            "report": {}
        }
        print(json.dumps(error_result))
        sys.exit(1)

    language = sys.argv[1].lower()
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        error_result = {
            "error": f"File not found: {file_path}",
            "optimizedCode": "",
            "linesRemoved": 0,
            "report": {}
        }
        print(json.dumps(error_result))
        sys.exit(1)

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        error_result = {
            "error": f"Failed to read file: {str(e)}",
            "optimizedCode": "",
            "linesRemoved": 0,
            "report": {}
        }
        print(json.dumps(error_result))
        sys.exit(1)

    # Route to language-specific optimizer
    try:
        if language == 'python':
            from python_optimizer import optimize_python
            result = optimize_python(original_code)
        elif language == 'c':
            from c_optimizer import optimize_c
            result = optimize_c(original_code)
        elif language == 'cpp':
            from cpp_optimizer import optimize_cpp
            result = optimize_cpp(original_code)
        elif language == 'java':
            from java_optimizer import optimize_java
            result = optimize_java(original_code)
        else:
            error_result = {
                "error": f"Unsupported language: {language}",
                "optimizedCode": original_code,
                "linesRemoved": 0,
                "report": {}
            }
            print(json.dumps(error_result))
            sys.exit(1)

        # Calculate lines removed
        original_lines = len(original_code.split('\n'))
        optimized_lines = len(result['optimizedCode'].split('\n'))
        result['linesRemoved'] = max(0, original_lines - optimized_lines)

        # Output JSON result
        print(json.dumps(result, indent=None))

    except Exception as e:
        error_result = {
            "error": f"Optimization failed: {str(e)}",
            "optimizedCode": original_code,
            "linesRemoved": 0,
            "report": {"error": str(e)}
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    main()