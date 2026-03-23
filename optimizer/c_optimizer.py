"""
C Dead Code Optimizer
Removes unused variables, functions, unreachable code, and dead branches
"""

import re

def optimize_c(code):
    """
    Optimize C code by removing dead code
    """
    try:
        optimized_code = code
        
        # Remove unused variable declarations
        optimized_code = remove_unused_variables(optimized_code)
        
        # Remove dead branches (if (0) or if (false))
        optimized_code = remove_dead_branches(optimized_code)
        
        # Remove unreachable code after return
        optimized_code = remove_unreachable_code(optimized_code)
        
        # Remove redundant assignments
        optimized_code = remove_redundant_assignments(optimized_code)
        
        # Remove empty statements
        optimized_code = remove_empty_statements(optimized_code)
        
        # Clean up extra blank lines
        optimized_code = clean_blank_lines(optimized_code)
        
        # Generate report
        original_lines = len(code.split('\n'))
        optimized_lines = len(optimized_code.split('\n'))
        
        report = {
            "language": "c",
            "originalLines": original_lines,
            "optimizedLines": optimized_lines,
            "removedLines": original_lines - optimized_lines,
            "optimizations": [
                "Removed unused variables",
                "Removed dead branches (if(0), if(false))",
                "Removed unreachable code",
                "Removed redundant assignments"
            ]
        }
        
        return {
            "optimizedCode": optimized_code,
            "report": report
        }
        
    except Exception as e:
        return {
            "optimizedCode": code,
            "report": {
                "error": str(e),
                "note": "Code returned unchanged due to optimization error"
            }
        }

def remove_unused_variables(code):
    """Remove simple unused variable declarations"""
    lines = code.split('\n')
    optimized_lines = []
    
    # Pattern for simple variable declarations: type name;
    var_decl_pattern = re.compile(r'^\s*(int|char|float|double|void|long|short)\s+\w+\s*;\s*$')
    
    for line in lines:
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            optimized_lines.append(line)
            continue
        
        # Check if it's a simple unused variable declaration
        # This is a conservative check - we only remove obviously unused ones
        if var_decl_pattern.match(line):
            # Check if variable is used later (simple check)
            var_name = re.search(r'(\w+)\s*;', line)
            if var_name:
                var = var_name.group(1)
                # Check if variable appears elsewhere (excluding the declaration)
                remaining_code = '\n'.join(lines[lines.index(line) + 1:])
                if var not in remaining_code or remaining_code.count(var) == 0:
                    # Variable not used, skip this line
                    continue
        
        optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)

def remove_dead_branches(code):
    """Remove dead branches like if(0) or if(false)"""
    lines = code.split('\n')
    optimized_lines = []
    skip_until_brace = 0
    brace_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check for if(0) or if(false)
        if re.match(r'^\s*if\s*\(\s*(0|false|FALSE)\s*\)', stripped):
            # Skip until matching closing brace
            brace_count = stripped.count('{') - stripped.count('}')
            skip_until_brace = brace_count
            if skip_until_brace <= 0:
                # Single line if, skip it
                i += 1
                continue
            i += 1
            continue
        
        if skip_until_brace > 0:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                skip_until_brace = 0
            i += 1
            continue
        
        optimized_lines.append(line)
        i += 1
    
    return '\n'.join(optimized_lines)

def remove_unreachable_code(code):
    """Remove code after return statements"""
    lines = code.split('\n')
    optimized_lines = []
    found_return = False
    
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\s*return\s*', stripped):
            found_return = True
            optimized_lines.append(line)
        elif found_return and stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
            # Check if it's a closing brace
            if stripped == '}' or stripped.startswith('}'):
                found_return = False
                optimized_lines.append(line)
            # Otherwise skip unreachable code
        else:
            optimized_lines.append(line)
            if stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                found_return = False
    
    return '\n'.join(optimized_lines)

def remove_redundant_assignments(code):
    """Remove redundant assignments (x = x;)"""
    pattern = r'(\w+)\s*=\s*\1\s*;'
    return re.sub(pattern, '', code)

def remove_empty_statements(code):
    """Remove empty statements (just semicolons)"""
    lines = code.split('\n')
    optimized_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped == ';' or stripped == '':
            # Skip empty lines and standalone semicolons
            if not stripped:
                optimized_lines.append(line)
            continue
        optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)

def clean_blank_lines(code):
    """Remove excessive blank lines (more than 2 consecutive)"""
    lines = code.split('\n')
    optimized_lines = []
    blank_count = 0
    
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                optimized_lines.append(line)
        else:
            blank_count = 0
            optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)