# Sloppy

**Python AI Slop Detector** - Find over-engineering, hallucinations, and dead code in Python codebases.

Sloppy detects "AI slop" patterns commonly produced by LLMs: over-engineering, hallucinated imports, placeholder functions, copy-paste code, and more.

## Installation

```bash
pip install sloppy
```

## Quick Start

```bash
# Scan current directory
sloppy .

# Scan specific files/directories
sloppy src/ tests/

# Output JSON report
sloppy --output report.json

# Only show high severity issues
sloppy --severity high

# CI mode (exit 1 if issues found)
sloppy --ci --max-score 50
```

## What It Detects

### Axis 1: Noise (Information Utility)
- Redundant comments that restate code
- Empty/generic docstrings
- Debug print statements and breakpoints
- Commented-out code blocks

### Axis 2: Lies (Information Quality)  
- Hallucinated imports (non-existent packages)
- Placeholder functions (`pass`, `...`, `NotImplementedError`)
- Mutable default arguments
- TODO/FIXME placeholders

### Axis 3: Soul (Style/Taste)
- Overconfident comments ("Obviously", "Simply")
- Hedging comments ("Should work", "Hopefully")
- God functions (>50 lines, >5 parameters)
- Deep nesting (>4 levels)

### Structural Anti-Patterns
- Single-method classes
- Bare/broad exception handlers
- Unused imports
- Duplicate code across files

## Output

```
SLOPPY INDEX
════════════════════════════════════════════════
Information Utility (Noise)    : 24 pts
Information Quality (Lies)     : 105 pts  
Style / Taste (Soul)           : 31 pts
Structural Issues              : 45 pts
────────────────────────────────────────────────
TOTAL SLOP SCORE               : 205 pts

Verdict: SLOPPY - This codebase needs cleanup
```

## Configuration

Configure via `pyproject.toml`:

```toml
[tool.sloppy]
exclude = ["tests/*", "migrations/*"]
disable = ["magic_number", "single_letter_var"]
severity_threshold = "medium"
```

## License

MIT
