"""Output reporters for terminal and JSON."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sloppy.patterns.base import Issue
    from sloppy.scoring import SlopScore


class Reporter(ABC):
    """Base reporter class."""
    
    @abstractmethod
    def report(self, issues: list["Issue"], score: "SlopScore") -> None:
        """Report issues and score."""
        pass


class TerminalReporter(Reporter):
    """Terminal output reporter."""
    
    def __init__(self, format_style: str = "detailed", min_severity: str = "low"):
        self.format_style = format_style
        self.min_severity = min_severity
    
    def report(self, issues: list["Issue"], score: "SlopScore") -> None:
        """Print report to terminal."""
        if not issues:
            print("No issues found. Clean code!")
            self._print_score(score)
            return
        
        # Group by severity
        by_severity: dict[str, list["Issue"]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }
        
        for issue in issues:
            by_severity[issue.severity.value].append(issue)
        
        # Print issues by severity
        for severity in ["critical", "high", "medium", "low"]:
            severity_issues = by_severity[severity]
            if not severity_issues:
                continue
            
            print(f"\n{severity.upper()} ({len(severity_issues)} issues)")
            print("=" * 60)
            
            for issue in severity_issues[:20]:  # Limit to 20 per severity
                self._print_issue(issue)
            
            if len(severity_issues) > 20:
                print(f"  ... and {len(severity_issues) - 20} more")
        
        self._print_score(score)
    
    def _print_issue(self, issue: "Issue") -> None:
        """Print a single issue."""
        location = f"{issue.file}:{issue.line}"
        if self.format_style == "compact":
            print(f"  {location}  {issue.pattern_id}: {issue.message}")
        else:
            print(f"  {location}  {issue.pattern_id}")
            print(f"    {issue.message}")
            if issue.code:
                print(f"    > {issue.code[:80]}")
    
    def _print_score(self, score: "SlopScore") -> None:
        """Print the score summary."""
        print("\n")
        print("SLOPPY INDEX")
        print("=" * 50)
        print(f"Information Utility (Noise)    : {score.noise} pts")
        print(f"Information Quality (Lies)     : {score.quality} pts")
        print(f"Style / Taste (Soul)           : {score.style} pts")
        print(f"Structural Issues              : {score.structure} pts")
        print("-" * 50)
        print(f"TOTAL SLOP SCORE               : {score.total} pts")
        print()
        print(f"Verdict: {score.verdict}")


class JSONReporter(Reporter):
    """JSON output reporter."""
    
    def report(self, issues: list["Issue"], score: "SlopScore") -> None:
        """Print JSON to stdout."""
        data = self._build_report(issues, score)
        print(json.dumps(data, indent=2))
    
    def write_file(self, issues: list["Issue"], score: "SlopScore", path: str) -> None:
        """Write JSON to file."""
        data = self._build_report(issues, score)
        Path(path).write_text(json.dumps(data, indent=2))
    
    def _build_report(self, issues: list["Issue"], score: "SlopScore") -> dict:
        """Build the JSON report structure."""
        return {
            "summary": {
                "total_issues": len(issues),
                "score": {
                    "noise": score.noise,
                    "quality": score.quality,
                    "style": score.style,
                    "structure": score.structure,
                    "total": score.total,
                },
                "verdict": score.verdict,
            },
            "issues": [
                {
                    "pattern_id": issue.pattern_id,
                    "severity": issue.severity.value,
                    "axis": issue.axis,
                    "file": str(issue.file),
                    "line": issue.line,
                    "column": issue.column,
                    "message": issue.message,
                    "code": issue.code,
                }
                for issue in issues
            ],
        }
