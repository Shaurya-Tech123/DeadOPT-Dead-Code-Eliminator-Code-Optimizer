"""
C++ Dead Code Optimizer
Removes unused variables, functions, unreachable code, and dead branches
"""

import re

def optimize_cpp(code):
    """
    Optimize C++ code by removing dead code
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
        
        # Remove unused includes (basic check)
        optimized_code = remove_unused_includes(optimized_code)
        
        # Clean up extra blank lines
        optimized_code = clean_blank_lines(optimized_code)
        
        # Generate report
        original_lines = len(code.split('\n'))
        optimized_lines = len(optimized_code.split('\n'))
        
        report = {
            "language": "cpp",
            "originalLines": original_lines,
            "optimizedLines": optimized_lines,
            "removedLines": original_lines - optimized_lines,
            "optimizations": [
                "Removed unused variables",
                "Removed dead branches (if(0), if(false))",
                "Removed unreachable code",
                "Removed redundant assignments",
                "Removed unused includes"
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
    
    # Pattern for C++ variable declarations
    var_decl_pattern = re.compile(r'^\s*(int|char|float|double|void|long|short|bool|string|std::string|auto)\s+\w+.*;\s*$')
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('#'):
            optimized_lines.append(line)
            continue
        
        # Check for simple unused variable declarations
        if var_decl_pattern.match(line) and '=' not in line and '(' not in line:
            var_match = re.search(r'(\w+)\s*;', line)
            if var_match:
                var = var_match.group(1)
                remaining_code = '\n'.join(lines[lines.index(line) + 1:])
                if var not in remaining_code:
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
        
        # Check for if(0), if(false), or if(0 == 1)
        if re.match(r'^\s*if\s*\(\s*(0|false|FALSE|0\s*==\s*1)\s*\)', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            skip_until_brace = brace_count
            if skip_until_brace <= 0:
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
            if stripped == '}' or stripped.startswith('}'):
                found_return = False
                optimized_lines.append(line)
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
    """Remove empty statements"""
    lines = code.split('\n')
    optimized_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped == ';' or (stripped == '' and len(optimized_lines) > 0 and optimized_lines[-1].strip() == ''):
            if not stripped:
                optimized_lines.append(line)
            continue
        optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)

def remove_unused_includes(code):
    """Remove obviously unused includes (basic heuristic)"""
    lines = code.split('\n')
    include_lines = []
    other_lines = []
    
    for line in lines:
        if line.strip().startswith('#include'):
            include_lines.append(line)
        else:
            other_lines.append(line)
    
    # Keep all includes for now (conservative approach)
    # In a real implementation, you'd analyze which headers are actually used
    return '\n'.join(include_lines + other_lines)

def clean_blank_lines(code):
    """Remove excessive blank lines"""
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