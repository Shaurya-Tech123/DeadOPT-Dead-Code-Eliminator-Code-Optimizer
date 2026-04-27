"""
Symbol table generation for DeadOPT.
"""

from __future__ import annotations

import ast
import re
from typing import Dict, List


def generate_symbol_table(language: str, code: str) -> List[Dict]:
    language = language.lower()
    if language == "python":
        return _python_symbol_table(code)
    if language in {"c", "cpp", "java"}:
        return _curly_symbol_table(code)
    return []


def _python_symbol_table(code: str) -> List[Dict]:
    tree = ast.parse(code)
    symbols: Dict[str, Dict] = {}
    scope_stack: List[str] = ["global"]

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            symbols[node.name] = {
                "name": node.name,
                "type": "function",
                "scope": scope_stack[-1],
                "lineDeclared": node.lineno,
                "usageCount": symbols.get(node.name, {}).get("usageCount", 0),
            }
            scope_stack.append("local")
            for arg in node.args.args:
                symbols[arg.arg] = {
                    "name": arg.arg,
                    "type": "parameter",
                    "scope": "local",
                    "lineDeclared": arg.lineno,
                    "usageCount": symbols.get(arg.arg, {}).get("usageCount", 0),
                }
            self.generic_visit(node)
            scope_stack.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)  # type: ignore[arg-type]

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    inferred_type = type(node.value).__name__.replace("Constant", "literal")
                    symbols[target.id] = {
                        "name": target.id,
                        "type": inferred_type,
                        "scope": scope_stack[-1],
                        "lineDeclared": node.lineno,
                        "usageCount": symbols.get(target.id, {}).get("usageCount", 0),
                    }
            self.generic_visit(node)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load):
                if node.id not in symbols:
                    symbols[node.id] = {
                        "name": node.id,
                        "type": "unknown",
                        "scope": scope_stack[-1],
                        "lineDeclared": getattr(node, "lineno", 0),
                        "usageCount": 0,
                    }
                symbols[node.id]["usageCount"] += 1

    Visitor().visit(tree)
    return list(symbols.values())


def _curly_symbol_table(code: str) -> List[Dict]:
    lines = code.splitlines()
    symbols: Dict[str, Dict] = {}
    usage_counts: Dict[str, int] = {}

    token_pattern = re.compile(r"\b[A-Za-z_]\w*\b")
    decl_pattern = re.compile(
        r"^\s*(?:(?:public|private|protected)\s+)?(?:(?:static)\s+)?(?:final\s+)?"
        r"(?:int|char|float|double|long|short|bool|boolean|String|void|auto|size_t)\s+([A-Za-z_]\w*)"
    )

    depth = 0
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            depth += line.count("{") - line.count("}")
            continue

        for token in token_pattern.findall(line):
            usage_counts[token] = usage_counts.get(token, 0) + 1

        match = decl_pattern.match(stripped)
        if match:
            name = match.group(1)
            symbol_type = "function" if "(" in stripped and ")" in stripped else "variable"
            symbols[name] = {
                "name": name,
                "type": symbol_type,
                "scope": "global" if depth == 0 else "local",
                "lineDeclared": index,
                "usageCount": 0,
            }

        depth += line.count("{") - line.count("}")

    for name, symbol in symbols.items():
        symbol["usageCount"] = max(0, usage_counts.get(name, 0) - 1)
    return list(symbols.values())
