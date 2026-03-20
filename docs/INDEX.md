# pytest-doctor Documentation Index

Complete documentation for pytest-doctor: Test suite analysis and improvement tool for Python.

**Created:** March 20, 2026  
**Total Files:** 13 markdown documents  
**Total Content:** 15,588 words + 5,276 lines

## 📑 All Documents

### Navigation & Overview
1. **README.md** (1,448 W) - Master index and navigation hub
2. **OVERVIEW.md** (662 W) - Quick introduction and features
3. **DOCUMENTATION_MAP.md** - Visual navigation guide
4. **DOCUMENTATION_SUMMARY.md** - Complete overview of all docs
5. **INDEX.md** - This file

### Core Concepts
6. **ARCHITECTURE.md** - Minimal tool-backed architecture
7. **RULES.md** - Diagnostic categories and guidance
8. **SCORING.md** - 0-100 health score calculation

### Analysis Features
9. **GAP_DETECTION.md** - Finding untested code paths
10. **EDGE_CASES.md** - Detecting missing test scenarios

### Usage & Integration
11. **CLI.md** (1,059 W) - Command-line interface guide
12. **API.md** (1,140 W) - Python API documentation
13. **CONFIG.md** (1,140 W) - Configuration options
14. **LLM_AGENTS.md** (1,429 W) - AI agent integration
15. **MIGRATION_TO_MINIMAL_ARCHITECTURE.md** - Legacy-to-minimal migration guide

## 🎯 Quick Navigation

### By Usage
- **[CLI.md](./CLI.md)** - How to run from command line
- **[API.md](./API.md)** - How to use from Python code
- **[CONFIG.md](./CONFIG.md)** - How to customize behavior
- **[LLM_AGENTS.md](./LLM_AGENTS.md)** - How to integrate with agents

### By Feature
- **[RULES.md](./RULES.md)** - Diagnostic rules and categories
- **[GAP_DETECTION.md](./GAP_DETECTION.md)** - Finding untested functions/branches
- **[EDGE_CASES.md](./EDGE_CASES.md)** - Finding missing edge case tests
- **[SCORING.md](./SCORING.md)** - Understanding the health score

### By Role
- **Test Engineer** → [RULES.md](./RULES.md) → [GAP_DETECTION.md](./GAP_DETECTION.md) → [EDGE_CASES.md](./EDGE_CASES.md)
- **Developer** → [API.md](./API.md) → [CONFIG.md](./CONFIG.md) → [ARCHITECTURE.md](./ARCHITECTURE.md)
- **DevOps** → [CLI.md](./CLI.md) → [CONFIG.md](./CONFIG.md) → CI/CD sections
- **Agent Builder** → [LLM_AGENTS.md](./LLM_AGENTS.md) → [API.md](./API.md) → [GAP_DETECTION.md](./GAP_DETECTION.md)

## 📚 Document Summaries

### OVERVIEW.md
**Purpose:** Quick introduction to pytest-doctor

What's covered:
- What the tool does (3 levels of analysis)
- Health score (0-100)
- Quick start (CLI and Python)
- Key features
- How agents use it
- Links to detailed docs

**When to read:** First! (5 minutes)

---

### ARCHITECTURE.md
**Purpose:** Understand the minimal architecture that reuses existing tools

What's covered:
- Four-pass pipeline (lint, coverage, dead code, complexity)
- Reused tools (`ruff`, `coverage`, `vulture`, `pytest-deadfixtures`, `radon`)
- Unified diagnostic contract
- Scoring and reporting flow
- Adapter-based extension strategy

**When to read:** Want to understand how it works (15 minutes)

---

### RULES.md
**Purpose:** Rule and diagnostic guidance

What's covered:
- 7 rule categories:
  1. Structure (7 rules) - Naming, organization
  2. Assertions (6 rules) - Clarity, type checking
  3. Fixtures (5 rules) - Scope, dependencies
  4. Mocking (5 rules) - Specs, patches
  5. Performance (3 rules) - Speed, optimization
  6. Maintainability (6 rules) - Duplication, clarity
  7. Coverage (4 rules) - Metrics
- Each rule: severity, examples, explanation
- Configuration for each rule
- How rules affect scoring

**When to read:** Want to improve test quality (20 minutes)

---

### GAP_DETECTION.md
**Purpose:** Find untested code and missing test coverage

What's covered:
- 8 gap types:
  1. Untested functions (0% coverage)
  2. Uncovered branches (if/else/except)
  3. Missing exception tests
  4. Uncovered exceptions
  5. State transition gaps
  6. Partial function coverage
  7. Dead test code
  8. Unreachable assertions
- Detection strategy for each
- Real code examples
- Test suggestions with templates
- Implementation details

**When to read:** Want to find untested code (15 minutes)

---

### EDGE_CASES.md
**Purpose:** Identify missing edge case tests

What's covered:
- Edge case suggestion categories:
  1. Numeric (zero, negative, overflow, NaN)
  2. Collections (empty, single, duplicates, large)
  3. Strings (empty, unicode, special chars)
  4. State (init, cleanup, transitions)
  5. Resources (exhaustion, timeout)
  6. Errors (missing file, permission)
  7. Type coercion (None, wrong type)
- Multiple examples per category
- Detection algorithms
- Test generation hints
- Configuration

**When to read:** Want to find missing test scenarios (15 minutes)

---

### SCORING.md
**Purpose:** Understand the 0-100 health score

What's covered:
- Score ranges and labels
- Scoring formula breakdown
- Coverage penalty (0-30 points)
- Quality penalty (per rule)
- Gap penalty (per gap type)
- Complete calculation examples
- Score distribution data
- Configuration of scoring weights
- Score improvement strategies

**When to read:** Want to understand your score (10 minutes)

---

### CLI.md
**Purpose:** Command-line usage guide

What's covered:
- Installation
- Basic usage (`pytest-doctor ./tests`)
- 14 command options with descriptions
- 8 usage examples (JSON, verbose, diff, etc.)
- Output formats (text, JSON, HTML)
- Configuration file handling
- Exit codes
- Environment variables
- CI/CD integration (GitHub Actions, GitLab, Jenkins)
- Pre-commit hooks
- Troubleshooting
- Color output

**When to read:** Want to use from command line (15 minutes)

---

### API.md
**Purpose:** Python API documentation

What's covered:
- Installation
- `diagnose()` function signature
- Results and data structures
- 10 usage examples
- Error handling
- Coverage analysis
- Gap analysis
- Score breakdown
- Filtering by category
- Multi-package analysis
- Integration patterns
- Advanced API
- Type hints
- Performance optimization

**When to read:** Want to use from Python code (15 minutes)

---

### CONFIG.md
**Purpose:** Configuration options and customization

What's covered:
- Config file locations
- Basic and full examples
- 5 configuration sections:
  1. coverage (enabled, minimum, exclude)
  2. gaps (detection options)
  3. rules (per-rule config)
  4. ignore (rules and files)
  5. scoring (weights, penalties)
- Environment variables
- pyproject.toml and setup.cfg support
- Examples for different scenarios
- Validation

**When to read:** Want to customize behavior (12 minutes)

---

### LLM_AGENTS.md
**Purpose:** AI agent integration guide

What's covered:
- 4 phases of agent workflow
- Structured output for agents
- 4 integration workflows:
  1. Fix all gaps
  2. Improve coverage
  3. Fix quality issues
  4. Iterative improvement
- 3 agent integration examples (Claude, Cursor, OpenCode)
- Prompt template for agents
- 5 best practices
- Progress monitoring
- Verification patterns

**When to read:** Want to build agent workflows (15 minutes)

---

### DOCUMENTATION_MAP.md
**Purpose:** Visual navigation guide

What's covered:
- Document hierarchy tree
- Learning paths by role
- Document purposes table
- Cross-reference network
- Reading recommendations (15 min, 30 min, 2+ hour paths)
- Finding information guide
- Table of contents for each document
- Statistics

**When to read:** Want visual navigation (5 minutes)

---

### DOCUMENTATION_SUMMARY.md
**Purpose:** Complete overview of documentation

What's covered:
- All files with sizes and purposes
- Key features documented
- Organization strategy
- Content highlights
- Quick navigation guide
- Documentation completeness checklist
- File locations
- Next steps by role

**When to read:** Want overview of what's documented (10 minutes)

---

## 🔗 Key Cross-Links

### From README.md
- [OVERVIEW.md](./OVERVIEW.md) - Introduction
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [RULES.md](./RULES.md) - Diagnostic rules
- [GAP_DETECTION.md](./GAP_DETECTION.md) - Coverage gaps
- [EDGE_CASES.md](./EDGE_CASES.md) - Edge cases
- [SCORING.md](./SCORING.md) - Health score
- [CLI.md](./CLI.md) - Command-line
- [API.md](./API.md) - Python API
- [CONFIG.md](./CONFIG.md) - Configuration
- [LLM_AGENTS.md](./LLM_AGENTS.md) - Agent integration

### From every document
- Links to prerequisite concepts
- Links to related features
- Links to usage examples
- "See Also" sections at bottom

## 📊 Content Summary

### Diagnostic Rules
- **Source:** primarily reused tool diagnostics (Ruff, coverage, vulture, radon)
- **Normalized output:** one diagnostic schema across all passes
- **Severity levels:** 3 (Error, Warning, Info)

### Gap Types
- **Total:** 8 types
- **Categories:** Functions, Branches, Exceptions, State, Coverage, Dead code
- **Real examples:** Yes, for each type
- **Test suggestions:** Yes, with templates

### Edge Case Categories
- **Total:** 7 categories
- **Examples per category:** 20+ total
- **Detection algorithm:** Yes, for each
- **Test generation hints:** Yes

### Code Examples
- **Total:** 50+ examples
- **Good patterns:** Marked with ✅
- **Bad patterns:** Marked with ❌
- **Languages:** Python (pytest)

### Reference Tables
- **Total:** 30+ tables
- **Topics:** Rules, gaps, edge cases, CLI options, config options
- **Linked:** All cross-referenced

## 🎓 Learning Resources

### Quick Start (15 minutes)
1. [README.md](./README.md) (2 min) - Navigation
2. [OVERVIEW.md](./OVERVIEW.md) (5 min) - What it does
3. [CLI.md](./CLI.md#basic-usage) (5 min) - How to run
4. [RULES.md](./RULES.md#rule-categories) (3 min) - Key rules

### Comprehensive (2+ hours)
Read all 13 documents in order for complete understanding.

### By Role
- **Test Engineer:** RULES.md → GAP_DETECTION.md → EDGE_CASES.md
- **Developer:** API.md → CONFIG.md → ARCHITECTURE.md
- **DevOps:** CLI.md → CONFIG.md → CI/CD integration
- **Agent Builder:** LLM_AGENTS.md → API.md → GAP_DETECTION.md

## 📋 Complete Table of Contents

See [DOCUMENTATION_MAP.md](./DOCUMENTATION_MAP.md) for detailed TOC for each document.

## ✅ What's Documented

- ✅ Minimal pass architecture and tool reuse strategy
- ✅ Coverage and gap detection approach
- ✅ Edge-case guidance and suggestions
- ✅ Complete scoring algorithm
- ✅ Full CLI documentation
- ✅ Complete Python API
- ✅ Minimal configuration surface
- ✅ Agent integration workflows
- ✅ CI/CD integration examples
- ✅ Cross-linked navigation

## 🚀 Starting Points

**New to pytest-doctor?**
→ Start with [README.md](./README.md) or [OVERVIEW.md](./OVERVIEW.md)

**Want to use it?**
→ Go to [CLI.md](./CLI.md) or [API.md](./API.md)

**Want to improve tests?**
→ Read [RULES.md](./RULES.md) then [GAP_DETECTION.md](./GAP_DETECTION.md)

**Want to find missing tests?**
→ Read [EDGE_CASES.md](./EDGE_CASES.md)

**Want to build an agent?**
→ Read [LLM_AGENTS.md](./LLM_AGENTS.md)

**Want to understand everything?**
→ Follow [DOCUMENTATION_MAP.md](./DOCUMENTATION_MAP.md) learning paths

## 📁 File Organization

```
docs/
├── INDEX.md (this file)
├── README.md (master navigation)
├── OVERVIEW.md (introduction)
├── ARCHITECTURE.md (system design)
├── RULES.md (diagnostic rules)
├── GAP_DETECTION.md (gap detection)
├── EDGE_CASES.md (edge cases)
├── SCORING.md (health score)
├── CLI.md (command-line)
├── API.md (Python API)
├── CONFIG.md (configuration)
├── LLM_AGENTS.md (agent integration)
├── MIGRATION_TO_MINIMAL_ARCHITECTURE.md (migration guide)
├── DOCUMENTATION_MAP.md (visual guide)
└── DOCUMENTATION_SUMMARY.md (overview)
```

---

**Start exploring with [README.md](./README.md) or [OVERVIEW.md](./OVERVIEW.md)!**

All documents are fully cross-linked for easy navigation.
