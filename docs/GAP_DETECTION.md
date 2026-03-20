# pytest-doctor: Gap Detection Strategy

See [ARCHITECTURE.md](./ARCHITECTURE.md) for system overview.

Gap detection is the core differentiator of pytest-doctor. It identifies untested code paths, uncovered branches, and missing exception handling tests.

## Gap Categories

### 1. Untested Functions

**Category**: `gap/untested-functions`

Functions that have 0% code coverage - they're never called by tests.

#### Detection Strategy

```python
for each function in code:
    if coverage_for(function) == 0:
        add_gap(
            category="gap/untested-functions",
            function=function,
            severity="error"
        )
```

#### Example

**Source code** (`src/auth.py`):
```python
def validate_token(token: str) -> bool:
    """Validate JWT token"""
    try:
        jwt.decode(token, SECRET_KEY)
        return True
    except jwt.InvalidTokenError:
        return False

def refresh_token(token: str) -> str:
    """Refresh expired token"""
    # ... implementation
    return new_token
```

**Coverage data** shows `validate_token` is tested, but `refresh_token` is not.

**Gap reported**:
```json
{
  "type": "gap",
  "category": "gap/untested-functions",
  "file": "src/auth.py",
  "function": "refresh_token",
  "line": 11,
  "severity": "error",
  "message": "Function refresh_token has 0% coverage",
  "help": "This function is never called by tests",
  "suggestion": "Create test: test_refresh_token_renews_expired_token()"
}
```

See [RULES.md](./RULES.md) for related rules.

### 2. Uncovered Branches

**Category**: `gap/uncovered-branches`

Control flow paths that are never exercised, like unexecuted if/else or except blocks.

#### Detection Strategy

```python
for each branch in code:
    if coverage_for(branch) == 0:
        add_gap(
            category="gap/uncovered-branches",
            branch=branch,
            type=branch.type,  # "if", "else", "except", "loop"
            severity="error"
        )
```

#### Example

**Source code** (`src/payment.py`):
```python
def process_payment(amount: float, method: str) -> bool:
    if method == "credit_card":
        return charge_credit_card(amount)
    elif method == "paypal":
        return charge_paypal(amount)
    else:
        raise ValueError(f"Unknown payment method: {method}")
```

**Tests only cover**: credit_card and paypal paths

**Gap detected**: else branch never tested (unknown payment method error)

**Gap reported**:
```json
{
  "type": "gap",
  "category": "gap/uncovered-branches",
  "file": "src/payment.py",
  "function": "process_payment",
  "line": 8,
  "severity": "error",
  "branch_type": "else",
  "message": "Else branch handling unknown payment method is uncovered",
  "help": "This error path is never tested",
  "suggestion": "Create test: test_process_payment_raises_on_unknown_method()"
}
```

#### Branch Types

- **if branches**: Condition true/false paths
- **except branches**: Exception handlers
- **loop branches**: Loop body and break/continue paths
- **match branches**: Python 3.10+ match/case statements

### 3. Missing Exception Tests

**Category**: `gap/missing-exception-tests`

Functions that raise exceptions but those exceptions are never tested (caught in tests).

#### Detection Strategy

```python
for each function in code:
    exceptions_raised = extract_exceptions(function)
    exceptions_tested = find_exception_assertions(tests_covering(function))
    
    for exception in exceptions_raised:
        if exception not in exceptions_tested:
            add_gap(
                category="gap/missing-exception-tests",
                function=function,
                exception=exception,
                severity="error"
            )
```

#### Example

**Source code** (`src/email.py`):
```python
def send_email(to: str, subject: str) -> bool:
    """Send email, raise InvalidEmailError if to is invalid"""
    if not is_valid_email(to):
        raise InvalidEmailError(f"Invalid email: {to}")
    
    smtp.send(to, subject)
    return True

def validate_domain(domain: str) -> bool:
    """Validate domain, raise ValueError if invalid"""
    if not domain or domain.startswith("."):
        raise ValueError("Invalid domain format")
    return True
```

**Tests only check**: successful email sending

**Gaps detected**:
- `InvalidEmailError` never tested
- `ValueError` in validate_domain never tested

**Gaps reported**:
```json
[
  {
    "type": "gap",
    "category": "gap/missing-exception-tests",
    "file": "src/email.py",
    "function": "send_email",
    "exception": "InvalidEmailError",
    "line": 5,
    "severity": "error",
    "message": "Function raises InvalidEmailError but exception is never tested",
    "suggestion": "Create test: test_send_email_raises_on_invalid_email()"
  },
  {
    "type": "gap",
    "category": "gap/missing-exception-tests",
    "file": "src/email.py",
    "function": "validate_domain",
    "exception": "ValueError",
    "line": 12,
    "severity": "error",
    "message": "Function raises ValueError but exception is never tested",
    "suggestion": "Create test: test_validate_domain_raises_on_invalid_format()"
  }
]
```

### 4. Uncovered Exceptions

**Category**: `gap/uncovered-exception-handlers`

Try/except blocks where the except clause is never triggered.

#### Example

```python
def read_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {path}")
        return DEFAULT_CONFIG
```

**Gap reported if**: Tests never provide invalid JSON file or missing file

### 5. State Transition Gaps

**Category**: `gap/untested-state-transitions`

State machines where certain state transitions are never exercised.

#### Detection Strategy

1. Identify state machines (classes with state attributes)
2. Find state transition points (assignments changing state)
3. Determine which transitions are tested
4. Report untested transitions

#### Example

**State machine** (`src/order.py`):
```python
class Order:
    def __init__(self):
        self.status = "pending"  # pending → confirmed → processing → shipped → delivered
    
    def confirm(self):
        if self.status == "pending":
            self.status = "confirmed"
    
    def process(self):
        if self.status == "confirmed":
            self.status = "processing"
    
    def ship(self):
        if self.status == "processing":
            self.status = "shipped"
    
    def deliver(self):
        if self.status == "shipped":
            self.status = "delivered"
```

**Possible transitions**: pending → confirmed → processing → shipped → delivered

**Tested transitions**: pending → confirmed → processing

**Gaps detected**:
- shipping (processing → shipped) not tested
- delivery (shipped → delivered) not tested
- out-of-order transitions not tested (e.g., confirm when already confirmed)

### 6. Partial Function Coverage

**Category**: `gap/partial-function-coverage`

Functions that are called but not all code paths are exercised.

#### Example

```python
def calculate_tax(amount: float, country: str) -> float:
    if country == "US":
        return amount * 0.07
    elif country == "EU":
        return amount * 0.19
    elif country == "UK":
        return amount * 0.20
    else:
        return 0
```

**Tested paths**: US and EU only (67% coverage)

**Gaps detected**:
- UK path uncovered
- else (unknown country) path uncovered

### 7. Dead Test Code

**Category**: `gap/dead-test-code`

Code in test files that's unreachable.

#### Examples

- Code after `pytest.skip()` or `pytest.fail()`
- Fixtures that are declared but never used
- Test functions that are never discovered
- Assertion code after `return` statement

#### Detection

```python
for each test file:
    for each statement after skip/fail/return:
        add_gap(category="gap/dead-test-code")
```

### 8. Unreachable Assertions

**Category**: `gap/unreachable-assertions`

Assertions that are never reached due to earlier failures or early returns.

#### Example

```python
def test_user_creation():
    user = create_user("john@example.com")
    assert user is not None
    assert user.email == "john@example.com"
    assert user.created_at is not None  # Unreachable if user is None
```

## Implementation Details

### AST Analysis

The gap detector uses Python's `ast` module to:

1. **Extract exceptions**:
```python
class ExceptionExtractor(ast.NodeVisitor):
    def visit_Raise(self, node):
        # Record raised exception
        self.exceptions.append(node.exc)
```

2. **Extract branches**:
```python
class BranchExtractor(ast.NodeVisitor):
    def visit_If(self, node):
        self.branches.append(("if", node))
        self.branches.append(("else", node.orelse))
    
    def visit_Try(self, node):
        self.branches.append(("try", node.body))
        for handler in node.handlers:
            self.branches.append(("except", handler))
```

3. **Extract state transitions**:
```python
class StateTransitionExtractor(ast.NodeVisitor):
    def visit_Assign(self, node):
        if node.targets[0].attr == self.state_var:
            self.transitions.append(node)
```

### Coverage Correlation

```python
class CoverageCorrelation:
    def correlate_function_to_coverage(func_info, coverage_data):
        func_lines = func_info.lines
        covered_lines = coverage_data.covered_lines
        
        uncovered_lines = func_lines - covered_lines
        if uncovered_lines:
            return partial_coverage(uncovered_lines)
        elif not func_lines & covered_lines:
            return no_coverage()
```

### Test Suggestion Generation

For each gap, generate a structured suggestion for LLM agents:

```python
@dataclass
class TestSuggestion:
    """Suggestion for creating a test to fill a gap"""
    test_name: str  # e.g. "test_validate_token_raises_on_expired"
    test_pattern: str  # "exception", "boundary", "state_transition"
    description: str  # What the test should do
    inputs: Dict  # Input values to test
    expected: str  # Expected outcome
    code_template: str  # Code snippet template
```

#### Example

```json
{
  "test_name": "test_send_email_raises_on_invalid_email",
  "test_pattern": "exception",
  "description": "Verify InvalidEmailError is raised for invalid email",
  "inputs": {
    "to": "not-an-email",
    "subject": "Test"
  },
  "expected": "Raises InvalidEmailError",
  "code_template": "with pytest.raises(InvalidEmailError):\n    send_email({to}, {subject})"
}
```

## Configuration

```json
{
  "gaps": {
    "enabled": true,
    "detection": {
      "untested-functions": true,
      "uncovered-branches": true,
      "missing-exceptions": true,
      "state-transitions": true,
      "dead-test-code": true,
      "partial-coverage": true
    },
    "minimum-coverage": 85,
    "severity-overrides": {
      "partial-coverage": "warning"
    }
  }
}
```

## Reporting

Gaps appear in results with structured information:

```python
result = diagnose("./tests")

for gap in result.gaps:
    print(f"{gap.category}: {gap.description}")
    print(f"  Location: {gap.location}")
    print(f"  Suggestion: {gap.test_suggestion.test_name}")
    print(f"  Template: {gap.test_suggestion.code_template}")
```

## See Also

- [EDGE_CASES.md](./EDGE_CASES.md) - Missing edge cases
- [RULES.md](./RULES.md) - Test quality rules
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [LLM_AGENTS.md](./LLM_AGENTS.md) - Using with LLM agents
