"""
DeadOPT improved optimizer pipeline.
Implements language-aware dead code elimination and report generation.
"""

from __future__ import annotations

import ast
import copy
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


TERMINAL_STMTS = (ast.Return, ast.Raise, ast.Break, ast.Continue)


def _count_lines(code: str) -> int:
    return len(code.splitlines()) if code else 0


def _estimate_complexity(code: str) -> int:
    patterns = [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bexcept\b", r"&&", r"\|\|"]
    score = 1
    for pattern in patterns:
        score += len(re.findall(pattern, code))
    return score


def _build_report(
    language: str,
    original_code: str,
    optimized_code: str,
    optimizations: List[str],
) -> Dict:
    original_lines = _count_lines(original_code)
    optimized_lines = _count_lines(optimized_code)
    removed_lines = max(0, original_lines - optimized_lines)
    original_complexity = _estimate_complexity(original_code)
    optimized_complexity = _estimate_complexity(optimized_code)
    complexity_delta = original_complexity - optimized_complexity
    improvement_pct = (removed_lines / max(1, original_lines)) * 100.0

    return {
        "summary": {
            "language": language,
            "originalLines": original_lines,
            "optimizedLines": optimized_lines,
            "linesRemoved": removed_lines,
            "improvementPercent": round(improvement_pct, 2),
        },
        "optimizationsApplied": sorted(set(optimizations)),
        "beforeAfter": {
            "before": original_code,
            "after": optimized_code,
        },
        "complexityImpact": {
            "before": original_complexity,
            "after": optimized_complexity,
            "delta": complexity_delta,
        },
    }


@dataclass
class PythonAnalysis:
    used_names: Set[str] = field(default_factory=set)
    imported_names: Set[str] = field(default_factory=set)
    function_defs: Dict[str, ast.FunctionDef] = field(default_factory=dict)
    called_functions: Set[str] = field(default_factory=set)
    assigned_names: Set[str] = field(default_factory=set)


class _PythonCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.analysis = PythonAnalysis()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.analysis.used_names.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.analysis.assigned_names.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.analysis.imported_names.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                continue
            self.analysis.imported_names.add(alias.asname or alias.name)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            self.analysis.called_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.analysis.called_functions.add(node.func.attr)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.analysis.function_defs[node.name] = node
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.analysis.function_defs[node.name] = node  # type: ignore[assignment]
        self.generic_visit(node)


def _is_safe_expr(expr: ast.AST) -> bool:
    safe_nodes = (
        ast.Constant,
        ast.Name,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Set,
    )
    return isinstance(expr, safe_nodes)


class _PythonOptimizer(ast.NodeTransformer):
    def __init__(self, analysis: PythonAnalysis, optimizations: List[str]) -> None:
        self.analysis = analysis
        self.optimizations = optimizations

    def _prune_unreachable(self, stmts: List[ast.stmt]) -> List[ast.stmt]:
        pruned: List[ast.stmt] = []
        terminate = False
        for stmt in stmts:
            if terminate:
                self.optimizations.append("Removed unreachable code after terminal statements")
                continue
            updated = self.visit(stmt)
            if updated is None:
                continue
            if isinstance(updated, list):
                pruned.extend(updated)
                if updated and isinstance(updated[-1], TERMINAL_STMTS):
                    terminate = True
            else:
                pruned.append(updated)
                if isinstance(updated, TERMINAL_STMTS):
                    terminate = True
        return pruned

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node.body = self._prune_unreachable(node.body)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.AST]:
        node.body = self._prune_unreachable(node.body)
        protected = {"main", "__init__", "__main__"}
        # Keep public top-level API functions by default.
        is_private = node.name.startswith("_") and not node.name.startswith("__")
        if node.name not in protected and is_private:
            if node.name not in self.analysis.called_functions:
                self.optimizations.append("Removed unused functions/methods")
                return None
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Optional[ast.AST]:
        node.body = self._prune_unreachable(node.body)
        protected = {"main", "__init__", "__main__"}
        is_private = node.name.startswith("_") and not node.name.startswith("__")
        if node.name not in protected and is_private:
            if node.name not in self.analysis.called_functions:
                self.optimizations.append("Removed unused functions/methods")
                return None
        return node

    def visit_Import(self, node: ast.Import) -> Optional[ast.AST]:
        kept = [a for a in node.names if (a.asname or a.name.split(".")[0]) in self.analysis.used_names]
        if not kept:
            self.optimizations.append("Removed unused imports/includes")
            return None
        node.names = kept
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Optional[ast.AST]:
        kept = [a for a in node.names if a.name == "*" or (a.asname or a.name) in self.analysis.used_names]
        if not kept:
            self.optimizations.append("Removed unused imports/includes")
            return None
        node.names = kept
        return node

    def visit_Assign(self, node: ast.Assign) -> Optional[ast.AST]:
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Name)
            and node.targets[0].id == node.value.id
        ):
            self.optimizations.append("Removed redundant assignments")
            return None

        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
            if target not in self.analysis.used_names and _is_safe_expr(node.value):
                self.optimizations.append("Removed unused variables")
                return None
        return node

    def visit_If(self, node: ast.If) -> Optional[ast.AST]:
        node.body = self._prune_unreachable(node.body)
        node.orelse = self._prune_unreachable(node.orelse)

        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            self.optimizations.append("Removed dead branches (if(0), if(false), equivalent constants)")
            if node.test.value:
                return node.body
            return node.orelse or None
        return node


def optimize_python(code: str) -> Tuple[str, List[str]]:
    tree = ast.parse(code)
    collector = _PythonCollector()
    collector.visit(tree)
    optimizations: List[str] = []

    optimized_tree = _PythonOptimizer(collector.analysis, optimizations).visit(copy.deepcopy(tree))
    ast.fix_missing_locations(optimized_tree)
    optimized_code = ast.unparse(optimized_tree)
    return optimized_code, optimizations


def optimize_curly_language(code: str, language: str) -> Tuple[str, List[str]]:
    lines = code.splitlines()
    optimizations: List[str] = []

    # Remove unused imports/includes.
    include_pattern = r"^\s*#include\s+[<\"].+[>\"]\s*$" if language in {"c", "cpp"} else r"^\s*import\s+[\w\.\*]+;\s*$"
    include_indices = [i for i, line in enumerate(lines) if re.match(include_pattern, line)]
    code_without_includes = [line for i, line in enumerate(lines) if i not in include_indices]
    code_payload = "\n".join(code_without_includes)

    retained = set()
    for i in include_indices:
        token_match = re.search(r"([A-Za-z_]\w+)(?:\.h|;)?", lines[i])
        if token_match and re.search(rf"\b{re.escape(token_match.group(1))}\b", code_payload):
            retained.add(i)
    if include_indices and len(retained) != len(include_indices):
        optimizations.append("Removed unused imports/includes")
    lines = [line for i, line in enumerate(lines) if i not in include_indices or i in retained]

    code_text = "\n".join(lines)

    if language == "java":
        code_text, java_opts = _optimize_java_simple(code_text)
        optimizations.extend(java_opts)
    else:
        # Remove dead branches (simple non-nested).
        before = code_text
        code_text = re.sub(
            r"if\s*\(\s*(?:0|false|FALSE)\s*\)\s*\{[^{}]*\}",
            "",
            code_text,
            flags=re.MULTILINE,
        )
        if code_text != before:
            optimizations.append("Removed dead branches (if(0), if(false), equivalent constants)")

    # Remove unreachable lines after return/break in same block.
    out_lines: List[str] = []
    block_kill_depth: Optional[int] = None
    depth = 0
    for line in code_text.splitlines():
        stripped = line.strip()
        current_depth = depth
        if block_kill_depth is not None and current_depth >= block_kill_depth and stripped and not stripped.startswith("//"):
            if stripped.startswith("}"):
                pass
            else:
                optimizations.append("Removed unreachable code after terminal statements")
                depth += line.count("{") - line.count("}")
                if depth < block_kill_depth:
                    block_kill_depth = None
                continue

        out_lines.append(line)
        delta = line.count("{") - line.count("}")
        if re.search(r"\b(return|break|continue)\b", stripped):
            # Do not propagate unreachable pruning when terminal is in a one-line block.
            if not ("{" in stripped and "}" in stripped):
                block_kill_depth = current_depth
        depth += delta
        if block_kill_depth is not None and depth < block_kill_depth:
            block_kill_depth = None

    code_text = "\n".join(out_lines)

    # Remove redundant assignments x = x;
    before = code_text
    code_text = re.sub(r"^\s*([A-Za-z_]\w*)\s*=\s*\1\s*;\s*$", "", code_text, flags=re.MULTILINE)
    if code_text != before:
        optimizations.append("Removed redundant assignments")

    # Variable/function declarations and usage detection.
    identifier_pattern = re.compile(r"\b[A-Za-z_]\w*\b")
    identifiers = identifier_pattern.findall(code_text)
    usage_count: Dict[str, int] = {}
    for token in identifiers:
        usage_count[token] = usage_count.get(token, 0) + 1

    decl_pattern = re.compile(
        r"^\s*(?:(?:public|private|protected)\s+)?(?:(?:static)\s+)?"
        r"(?:int|char|float|double|long|short|bool|boolean|String|void|auto|size_t)\s+([A-Za-z_]\w*)"
    )
    final_lines: List[str] = []
    for line in code_text.splitlines():
        stripped_line = line.strip()
        match = decl_pattern.match(stripped_line)
        if match:
            name = match.group(1)
            is_function = "(" in stripped_line and ")" in stripped_line and ("{" in stripped_line or stripped_line.endswith(";"))
            is_private_or_static = bool(re.search(r"\b(private|static)\b", stripped_line))
            is_simple_decl = stripped_line.endswith(";") and "(" not in stripped_line and "," not in stripped_line
            is_one_line_function = is_function and "{" in stripped_line and "}" in stripped_line

            if "main(" in stripped_line or name == "main":
                final_lines.append(line)
                continue

            if is_one_line_function and is_private_or_static and usage_count.get(name, 0) <= 1:
                optimizations.append("Removed unused functions/methods")
                continue

            # Avoid removing initialized declarations to preserve semantics.
            if is_simple_decl and usage_count.get(name, 0) <= 1:
                optimizations.append("Removed unused variables")
                continue
        final_lines.append(line)

    optimized_code = "\n".join(final_lines)
    optimized_code = re.sub(r"\n{3,}", "\n\n", optimized_code).strip() + ("\n" if optimized_code.strip() else "")
    return optimized_code, optimizations


def _java_strip_comments_and_strings(code: str) -> str:
    """
    Lightweight masking to avoid counting identifiers inside comments/strings.
    Replaces content with spaces but keeps newlines.
    """
    out: List[str] = []
    i = 0
    n = len(code)
    state = "code"  # code|line|block|string|char
    escape = False
    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                out.append("  ")
                i += 2
                state = "line"
                continue
            if ch == "/" and nxt == "*":
                out.append("  ")
                i += 2
                state = "block"
                continue
            if ch == '"':
                out.append(" ")
                i += 1
                state = "string"
                escape = False
                continue
            if ch == "'":
                out.append(" ")
                i += 1
                state = "char"
                escape = False
                continue
            out.append(ch)
            i += 1
            continue
        if state == "line":
            if ch == "\n":
                out.append("\n")
                i += 1
                state = "code"
            else:
                out.append(" ")
                i += 1
            continue
        if state == "block":
            if ch == "*" and nxt == "/":
                out.append("  ")
                i += 2
                state = "code"
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue
        if state in {"string", "char"}:
            if ch == "\n":
                out.append("\n")
                i += 1
                state = "code"
                escape = False
                continue
            if escape:
                out.append(" ")
                escape = False
                i += 1
                continue
            if ch == "\\":
                out.append(" ")
                escape = True
                i += 1
                continue
            if (state == "string" and ch == '"') or (state == "char" and ch == "'"):
                out.append(" ")
                i += 1
                state = "code"
                continue
            out.append(" ")
            i += 1
            continue
    return "".join(out)


def _optimize_java_simple(code_text: str) -> Tuple[str, List[str]]:
    """
    Simple + stable Java optimizer (brace-aware, line-based):
      - Remove unused methods (keep main + constructors)
      - Fold constant if(true/false) blocks (multi-line, brace-matched)
      - Remove unreachable code after return (handled later by shared pass too)
      - Remove basic unused local variable declarations (incl. literal init)
      - Remove redundant assignments x = x;
    """
    optimizations: List[str] = []
    lines = code_text.splitlines()

    masked = _java_strip_comments_and_strings(code_text)

    def normalize_else_blocks(src_lines: List[str]) -> List[str]:
        normalized: List[str] = []
        for ln in src_lines:
            m = re.match(r"^(\s*)}\s*else\s*\{\s*$", ln)
            if m:
                indent = m.group(1)
                normalized.append(indent + "}")
                normalized.append(indent + "else {")
            else:
                normalized.append(ln)
        return normalized

    # Normalize `} else {` into two lines (for safe folding).
    lines = normalize_else_blocks(lines)
    masked_lines = normalize_else_blocks(masked.splitlines())
    code_text = "\n".join(lines)
    masked = "\n".join(masked_lines)

    # --- Step A: remove unused methods (very conservative) ---
    class_match = re.search(r"\bclass\s+([A-Za-z_]\w*)", masked)
    class_name = class_match.group(1) if class_match else ""

    # method signature line (single-line header with opening brace)
    sig_re = re.compile(
        r"^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)\s+)*"
        r"(?:[\w<>\[\],.?]+\s+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{\s*$"
    )

    # collect method blocks by brace counting
    methods: List[Dict[str, int | str]] = []
    i = 0
    while i < len(lines):
        m = sig_re.match(masked_lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1)
        start = i
        depth = 0
        opened = False
        j = i
        while j < len(lines):
            depth += masked.splitlines()[j].count("{") - masked.splitlines()[j].count("}")
            if "{" in masked.splitlines()[j]:
                opened = True
            if opened and depth == 0:
                break
            j += 1
        if j >= len(lines):
            i += 1
            continue
        end = j
        methods.append({"name": name, "start": start, "end": end})
        i = end + 1

    # calls: any identifier followed by '(', excluding method declaration lines.
    masked_for_calls_lines = masked_lines[:]
    for m in methods:
        masked_for_calls_lines[int(m["start"])] = ""
    masked_for_calls = "\n".join(masked_for_calls_lines)
    call_names = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", masked_for_calls))
    kept = {"main"}
    if class_name:
        kept.add(class_name)  # constructor name

    to_remove = []
    for m in methods:
        name = str(m["name"])
        if name in kept:
            continue
        if name not in call_names:
            to_remove.append((int(m["start"]), int(m["end"])))

    if to_remove:
        optimizations.append("Removed unused functions/methods")
        for start, end in sorted(to_remove, reverse=True):
            del lines[start : end + 1]

    # refresh masked after method removals
    code_text = "\n".join(lines)
    masked = _java_strip_comments_and_strings(code_text)
    lines = normalize_else_blocks(code_text.splitlines())
    masked_lines = normalize_else_blocks(masked.splitlines())
    code_text = "\n".join(lines)
    masked = "\n".join(masked_lines)
    lines = code_text.splitlines()

    # --- Step B: constant if folding (brace-aware, supports multi-line blocks) ---
    def find_matching_brace(start_line: int) -> int:
        depth = 0
        opened = False
        k = start_line
        while k < len(lines):
            depth += masked_lines[k].count("{") - masked_lines[k].count("}")
            if "{" in masked_lines[k]:
                opened = True
            if opened and depth == 0:
                return k
            k += 1
        return -1

    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)if\s*\(\s*(true|false)\s*\)\s*\{\s*$", masked_lines[i])
        if not m:
            i += 1
            continue
        cond_true = m.group(2) == "true"
        then_start = i
        then_end = find_matching_brace(i)
        if then_end == -1:
            i += 1
            continue

        # check else
        k = then_end + 1
        while k < len(lines) and masked_lines[k].strip() == "":
            k += 1
        has_else = k < len(lines) and re.match(r"^\s*else\s*\{\s*$", masked_lines[k] or "")
        else_start = else_end = -1
        if has_else:
            else_start = k
            else_end = find_matching_brace(k)
            if else_end == -1:
                has_else = False

        then_body = lines[then_start + 1 : then_end]
        else_body = lines[else_start + 1 : else_end] if has_else else []
        replacement = then_body if cond_true else else_body

        cut_end = else_end if has_else else then_end
        del lines[then_start : cut_end + 1]
        for ins in reversed(replacement):
            lines.insert(then_start, ins)

        code_text = "\n".join(lines)
        masked = _java_strip_comments_and_strings(code_text)
        masked_lines = masked.splitlines()
        optimizations.append("Removed dead branches (if(true/false) constant folding)")
        i = max(0, then_start - 1)

    # --- Step C: redundant assignments ---
    new_lines: List[str] = []
    for ln in lines:
        if re.match(r"^\s*([A-Za-z_]\w*)\s*=\s*\1\s*;\s*$", ln):
            optimizations.append("Removed redundant assignments")
            continue
        new_lines.append(ln)
    lines = new_lines

    # --- Step D: basic unused locals (simple type decl, optional literal init) ---
    full_masked = _java_strip_comments_and_strings("\n".join(lines))
    decl_re = re.compile(
        r"^\s*(?:final\s+)?(?:byte|short|int|long|float|double|boolean|char|String)\s+([A-Za-z_]\w*)\s*(?:=\s*([^;]+))?;\s*$"
    )
    final_lines: List[str] = []
    for idx, ln in enumerate(lines):
        # Allow inline // comments on declarations.
        decl_part = ln.split("//", 1)[0].rstrip()
        m = decl_re.match(decl_part)
        if not m:
            final_lines.append(ln)
            continue
        name = m.group(1)
        init = (m.group(2) or "").strip()
        if init and not re.match(r"^(?:-?\d+(?:\.\d+)?|true|false|null|\"[^\"]*\"|'[^']*')$", init):
            final_lines.append(ln)
            continue
        remaining = "\n".join(full_masked.splitlines()[:idx] + [""] + full_masked.splitlines()[idx + 1 :])
        if re.search(rf"\b{re.escape(name)}\b", remaining) is None:
            optimizations.append("Removed unused variables")
            continue
        final_lines.append(ln)

    code_text = "\n".join(final_lines)
    code_text = re.sub(r"\n{3,}", "\n\n", code_text)
    return code_text, optimizations

def _java_simplify_constant_ifs(lines: List[str], optimizations: List[str]) -> List[str]:
    # Legacy helper kept for compatibility; the simplified Java optimizer no longer
    # uses this line-based block rewriter (it was too easy to break braces).
    return lines


def optimize_code(language: str, code: str) -> Dict:
    language = language.lower()
    if language == "python":
        optimized_code, optimizations = optimize_python(code)
    elif language in {"c", "cpp", "java"}:
        optimized_code, optimizations = optimize_curly_language(code, language)
    else:
        raise ValueError(f"Unsupported language: {language}")

    report = _build_report(language, code, optimized_code, optimizations)
    return {"optimizedCode": optimized_code, "report": report}
