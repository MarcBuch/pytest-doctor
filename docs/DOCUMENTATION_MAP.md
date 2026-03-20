# pytest-doctor Documentation Map

Visual navigation guide for the complete documentation set.

## 📍 Document Hierarchy

```
START HERE
    ↓
README.md (Master Index)
    ├─ Quick start
    ├─ Feature map
    ├─ Common tasks
    └─ Full navigation
    ↓
OVERVIEW.md (Introduction)
    └─ What is pytest-doctor?
       ├─ Feature overview
       ├─ Quick examples
       └─ Next steps
    
LEARNING PATHS DIVERGE:
    ├─→ ARCHITECTURE.md (How it works)
    │   ├─ Component design
    │   ├─ Data flow
    │   └─ Extension points
    │
    ├─→ CLI.md (Command-line usage)
    │   ├─ Installation
    │   ├─ Basic commands
    │   ├─ Options & flags
    │   └─ CI/CD integration
    │
    ├─→ API.md (Python API)
    │   ├─ Core functions
    │   ├─ Code examples
    │   └─ Advanced usage
    │
    ├─→ RULES.md (Quality checks)
    │   ├─ 40+ diagnostic rules
    │   ├─ Good/bad examples
    │   └─ Configuration
    │
    ├─→ GAP_DETECTION.md (Finding gaps)
    │   ├─ 6 gap types
    │   ├─ Real examples
    │   └─ Test suggestions
    │
    ├─→ EDGE_CASES.md (Missing tests)
    │   ├─ 7 edge case categories
    │   ├─ Concrete examples
    │   └─ Test generation
    │
    ├─→ SCORING.md (0-100 score)
    │   ├─ Score calculation
    │   ├─ Penalty breakdown
    │   └─ Examples
    │
    ├─→ CONFIG.md (Configuration)
    │   ├─ Config file options
    │   ├─ Customization
    │   └─ Examples
    │
    └─→ LLM_AGENTS.md (Agent integration)
        ├─ How agents use it
        ├─ Structured output
        ├─ Workflows
        └─ Examples
```

## 🎯 Quick Reference by Role

### Test Engineer
```
START → OVERVIEW.md
       → RULES.md (what to improve)
       → GAP_DETECTION.md (what's untested)
       → EDGE_CASES.md (missing scenarios)
       → SCORING.md (understand score)
```

### Developer
```
START → OVERVIEW.md
       → API.md (how to use)
       → CONFIG.md (customize)
       → ARCHITECTURE.md (understand system)
```

### DevOps Engineer
```
START → OVERVIEW.md
       → CLI.md (run tool)
       → CONFIG.md (setup)
       → CI/CD section in CLI.md
```

### AI Agent Builder
```
START → OVERVIEW.md
       → LLM_AGENTS.md (integration)
       → API.md (data structures)
       → GAP_DETECTION.md (gap types)
       → EDGE_CASES.md (suggestions)
```

## 📚 Document Purposes

| Document | Size | Focus | Use When... |
|----------|------|-------|-----------|
| **README.md** | 1.4K | Navigation | You need to find something |
| **OVERVIEW.md** | 662 W | Intro | Getting started |
| **ARCHITECTURE.md** | 1.3K | Design | Understanding how it works |
| **RULES.md** | 1.7K | Quality | Improving test quality |
| **GAP_DETECTION.md** | 1.2K | Gaps | Finding untested code |
| **EDGE_CASES.md** | 1.7K | Edge Cases | Finding missing tests |
| **SCORING.md** | 1.3K | Score | Understanding the score |
| **CLI.md** | 1.1K | Terminal | Running from command line |
| **API.md** | 1.1K | Code | Using from Python |
| **CONFIG.md** | 1.1K | Settings | Customizing behavior |
| **LLM_AGENTS.md** | 1.4K | Agents | Building agent workflows |

## 🔗 Cross-Reference Network

Every document links to:

### From OVERVIEW.md
- [ARCHITECTURE.md](./ARCHITECTURE.md) - system design
- [RULES.md](./RULES.md) - diagnostic rules
- [GAP_DETECTION.md](./GAP_DETECTION.md) - gap detection
- [EDGE_CASES.md](./EDGE_CASES.md) - edge cases
- [SCORING.md](./SCORING.md) - health score
- [CLI.md](./CLI.md) - command-line usage
- [API.md](./API.md) - Python API
- [CONFIG.md](./CONFIG.md) - configuration
- [LLM_AGENTS.md](./LLM_AGENTS.md) - agent integration

### From RULES.md
- [OVERVIEW.md](./OVERVIEW.md) - introduction
- [ARCHITECTURE.md](./ARCHITECTURE.md) - system design
- [SCORING.md](./SCORING.md) - how rules affect score
- [GAP_DETECTION.md](./GAP_DETECTION.md) - coverage gaps
- [EDGE_CASES.md](./EDGE_CASES.md) - edge cases
- [CONFIG.md](./CONFIG.md) - rule configuration

### From GAP_DETECTION.md
- [ARCHITECTURE.md](./ARCHITECTURE.md) - analyzer design
- [EDGE_CASES.md](./EDGE_CASES.md) - complementary feature
- [RULES.md](./RULES.md) - related rules
- [SCORING.md](./SCORING.md) - gap penalties
- [LLM_AGENTS.md](./LLM_AGENTS.md) - agent use

### From API.md
- [OVERVIEW.md](./OVERVIEW.md) - introduction
- [CLI.md](./CLI.md) - CLI alternative
- [CONFIG.md](./CONFIG.md) - configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - system design

## 🎓 Reading Recommendations

### 15-Minute Overview
1. OVERVIEW.md (5 min) - Feature overview
2. CLI.md basics (5 min) - How to run
3. RULES.md skim (5 min) - What gets checked

### 30-Minute Deep Dive
1. OVERVIEW.md (5 min)
2. GAP_DETECTION.md (8 min)
3. EDGE_CASES.md (8 min)
4. SCORING.md (5 min)
5. RULES.md skim (4 min)

### Complete Understanding (2+ hours)
Read all documents in order:
1. README.md - Navigation
2. OVERVIEW.md - Introduction
3. ARCHITECTURE.md - System design
4. RULES.md - All diagnostic rules
5. GAP_DETECTION.md - Gap detection
6. EDGE_CASES.md - Edge cases
7. SCORING.md - Score calculation
8. CLI.md - Command-line usage
9. API.md - Python API
10. CONFIG.md - Configuration
11. LLM_AGENTS.md - Agent integration

## 🔍 Finding Information

### I want to know about...

**Test Quality Rules**
→ RULES.md
  - Structure rules (section 1)
  - Assertion rules (section 2)
  - Fixture rules (section 3)
  - Mocking rules (section 4)
  - Performance rules (section 5)
  - Maintainability rules (section 6)
  - Coverage rules (section 7)

**Coverage Gaps**
→ GAP_DETECTION.md
  - Untested functions
  - Uncovered branches
  - Missing exceptions
  - State transitions
  - Partial coverage
  - Dead test code

**Edge Cases**
→ EDGE_CASES.md
  - Numeric edge cases
  - Collection edge cases
  - String edge cases
  - State edge cases
  - Resource edge cases
  - Error path edge cases
  - Type coercion edge cases

**How to Use**
→ CLI.md (command-line) or API.md (Python)

**Configuration**
→ CONFIG.md

**Scoring System**
→ SCORING.md

**System Design**
→ ARCHITECTURE.md

**Agent Integration**
→ LLM_AGENTS.md

## 📖 Table of Contents

### OVERVIEW.md (5 min read)
- What It Does
- Health Score
- Quick Start
- For LLM Agents
- Architecture
- Features
- Examples

### ARCHITECTURE.md (15 min read)
- System Design diagram
- Core Components (9 components)
- Data Flow diagram
- Key Interfaces
- Extension Points
- Performance
- Integration Points

### RULES.md (20 min read)
- Rule Categories (7 total)
- Structure Rules (7 rules)
- Assertion Rules (6 rules)
- Fixture Rules (5 rules)
- Mocking Rules (5 rules)
- Performance Rules (3 rules)
- Maintainability Rules (6 rules)
- Coverage Rules (4 rules)
- Rule Configuration
- Severity Levels
- Examples

### GAP_DETECTION.md (15 min read)
- Gap Categories (8 total)
- Untested Functions
- Uncovered Branches
- Missing Exception Tests
- Uncovered Exceptions
- State Transition Gaps
- Partial Function Coverage
- Dead Test Code
- Unreachable Assertions
- Implementation Details
- Configuration
- Reporting

### EDGE_CASES.md (15 min read)
- Edge Case Categories (7 total)
- Numeric Edge Cases
- Collection Edge Cases
- String Edge Cases
- State & Lifecycle Edge Cases
- Resource & Performance Edge Cases
- Error Path Edge Cases
- Type Coercion Edge Cases
- Detection Algorithm
- Reporting
- Configuration

### SCORING.md (10 min read)
- Score Ranges
- Scoring Formula
- Coverage Penalty
- Quality Penalty
- Gap Penalty
- Score Calculation
- Example Calculations (3 scenarios)
- Score Distribution
- Weighting Rationale
- Score Improvements (examples)
- Configuration
- Reporting

### CLI.md (15 min read)
- Installation
- Basic Usage
- Commands (scan)
- Options (14 options)
- Examples (8 examples)
- Configuration File
- Exit Codes
- Environment Variables
- CI/CD Integration (3 platforms + pre-commit)
- Troubleshooting
- Output Colors

### API.md (15 min read)
- Installation
- Basic Usage
- Core API (diagnose function)
- Results structure
- Examples (10 examples)
- Advanced API
- Type Hints
- Performance

### CONFIG.md (12 min read)
- Configuration File Location
- Basic Configuration (2 examples)
- Full Configuration Example
- Configuration Options (5 sections)
- Severity Levels
- Environment Variables
- pyproject.toml support
- setup.cfg support
- Config Precedence
- Examples (3 scenarios)
- Validation

### LLM_AGENTS.md (15 min read)
- How Agents Use pytest-doctor (4 phases)
- Structured Output (3 example structures)
- Agent Workflows (4 workflows)
- Agent Integration Examples (3 agents)
- Structured Prompt Template
- Best Practices (5 practices)
- Monitoring Agent Progress

## 📊 Documentation Statistics

| Metric | Value |
|--------|-------|
| Total Documents | 12 |
| Total Words | 15,588 |
| Total Sections | 100+ |
| Code Examples | 50+ |
| Diagnostic Rules | 37 |
| Gap Types | 8 |
| Edge Case Categories | 7 |
| Reference Tables | 30+ |

## 🚀 Getting Started

### Absolute First-Timer
**Start Here:** README.md → OVERVIEW.md → CLI.md

### Experienced Developer
**Start Here:** OVERVIEW.md → API.md → CONFIG.md

### Test Automation Expert
**Start Here:** OVERVIEW.md → RULES.md → GAP_DETECTION.md → EDGE_CASES.md

### Building an Agent
**Start Here:** OVERVIEW.md → LLM_AGENTS.md → API.md → GAP_DETECTION.md

---

**All documentation cross-linked for easy navigation.**

Start with **README.md** or **OVERVIEW.md**!
