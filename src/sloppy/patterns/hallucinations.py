"""Axis 2: Information Quality (Hallucinations) patterns."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List

from sloppy.patterns.base import RegexPattern, ASTPattern, Severity, Issue


class TodoPlaceholder(RegexPattern):
    """Detect TODO/FIXME implementation placeholders."""
    
    id = "todo_placeholder"
    severity = Severity.HIGH
    axis = "quality"
    message = "TODO placeholder - implementation needed"
    pattern = re.compile(
        r'#\s*(TODO|FIXME|XXX|HACK)\s*:?\s*.*(implement|add|finish|complete|fill in|your code|logic here)',
        re.IGNORECASE
    )


class AssumptionComment(RegexPattern):
    """Detect assumption comments indicating unverified code."""
    
    id = "assumption_comment"
    severity = Severity.HIGH
    axis = "quality"
    message = "Assumption in code - verify before shipping"
    pattern = re.compile(
        r'#\s*(assuming|assumes?|presumably|apparently|i think|we think|should be|might be)\b',
        re.IGNORECASE
    )


class MagicNumber(RegexPattern):
    """Detect unexplained magic numbers."""
    
    id = "magic_number"
    severity = Severity.MEDIUM
    axis = "quality"
    message = "Magic number - extract to named constant"
    pattern = re.compile(
        r'(?<![.\w])\b(?!0\b|1\b|2\b|100\b|1000\b|True\b|False\b|None\b)'
        r'\d{2,}\b(?!\.\d)'  # 2+ digit numbers not followed by decimal
    )


class PassPlaceholder(ASTPattern):
    """Detect placeholder functions with just pass."""
    
    id = "pass_placeholder"
    severity = Severity.HIGH
    axis = "quality"
    message = "Placeholder function with pass - implementation needed"
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    
    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: List[str],
    ) -> List[Issue]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        # Check if body is just pass (optionally with docstring)
        body = node.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            return [self.create_issue_from_node(node, file, code=f"def {node.name}(...): pass")]
        
        # Docstring + pass
        if len(body) == 2:
            has_docstring = (
                isinstance(body[0], ast.Expr) and
                isinstance(body[0].value, ast.Constant) and
                isinstance(body[0].value.value, str)
            )
            if has_docstring and isinstance(body[1], ast.Pass):
                return [self.create_issue_from_node(node, file, code=f"def {node.name}(...): pass")]
        
        return []


class EllipsisPlaceholder(ASTPattern):
    """Detect placeholder functions with just ellipsis."""
    
    id = "ellipsis_placeholder"
    severity = Severity.HIGH
    axis = "quality"
    message = "Placeholder function with ... - implementation needed"
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    
    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: List[str],
    ) -> List[Issue]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        body = node.body
        
        # Just ellipsis
        if len(body) == 1:
            if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if body[0].value.value is ...:
                    return [self.create_issue_from_node(node, file, code=f"def {node.name}(...): ...")]
        
        # Docstring + ellipsis
        if len(body) == 2:
            has_docstring = (
                isinstance(body[0], ast.Expr) and
                isinstance(body[0].value, ast.Constant) and
                isinstance(body[0].value.value, str)
            )
            if has_docstring and isinstance(body[1], ast.Expr):
                if isinstance(body[1].value, ast.Constant) and body[1].value.value is ...:
                    return [self.create_issue_from_node(node, file, code=f"def {node.name}(...): ...")]
        
        return []


class NotImplementedPlaceholder(ASTPattern):
    """Detect placeholder functions that just raise NotImplementedError."""
    
    id = "notimplemented_placeholder"
    severity = Severity.MEDIUM
    axis = "quality"
    message = "Function raises NotImplementedError - implementation needed"
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    
    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: List[str],
    ) -> List[Issue]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        body = node.body
        
        # Check last statement for raise NotImplementedError
        effective_body = body
        if len(body) >= 1:
            # Skip docstring
            if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    effective_body = body[1:]
        
        if len(effective_body) == 1 and isinstance(effective_body[0], ast.Raise):
            exc = effective_body[0].exc
            if isinstance(exc, ast.Call):
                if isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                    return [self.create_issue_from_node(
                        node, file, code=f"def {node.name}(...): raise NotImplementedError"
                    )]
            elif isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return [self.create_issue_from_node(
                    node, file, code=f"def {node.name}(...): raise NotImplementedError"
                )]
        
        return []


class MutableDefaultArg(ASTPattern):
    """Detect mutable default arguments."""
    
    id = "mutable_default_arg"
    severity = Severity.CRITICAL
    axis = "quality"
    message = "Mutable default argument - use None and initialize inside function"
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    
    def check_node(
        self,
        node: ast.AST,
        file: Path,
        source_lines: List[str],
    ) -> List[Issue]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        issues = []
        
        # Check positional defaults
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                issues.append(self.create_issue_from_node(
                    default, file,
                    code=f"def {node.name}(...={self._get_default_repr(default)})",
                    message=f"Mutable default argument ({self._get_default_repr(default)}) - use None instead"
                ))
        
        # Check keyword-only defaults
        for default in node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                issues.append(self.create_issue_from_node(
                    default, file,
                    code=f"def {node.name}(...={self._get_default_repr(default)})",
                    message=f"Mutable default argument ({self._get_default_repr(default)}) - use None instead"
                ))
        
        return issues
    
    def _get_default_repr(self, node: ast.AST) -> str:
        if isinstance(node, ast.List):
            return "[]"
        elif isinstance(node, ast.Dict):
            return "{}"
        elif isinstance(node, ast.Set):
            return "set()"
        return "..."


HALLUCINATION_PATTERNS = [
    TodoPlaceholder(),
    AssumptionComment(),
    MagicNumber(),
    PassPlaceholder(),
    EllipsisPlaceholder(),
    NotImplementedPlaceholder(),
    MutableDefaultArg(),
]
