# pytest-doctor: Edge Case Detection

See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap detection overview.

Edge case detection identifies missing tests for boundary values, special inputs, and corner cases that could cause subtle bugs.

## Edge Case Categories

### 1. Numeric Edge Cases

**Category**: `gap/missing-numeric-edge-cases`

Tests for boundary values and special numeric conditions.

#### Common Cases

| Case | Example | Input | Note |
|------|---------|-------|------|
| **Zero** | Division by zero | `x = 0` | Often causes special behavior |
| **Negative** | Negative indices | `x = -1` | Many functions assume positive |
| **Boundary** | Off-by-one errors | `x = limit - 1, x = limit + 1` | Array boundaries |
| **Maximum** | Integer overflow | `x = sys.maxsize` | Wraparound bugs |
| **Minimum** | Underflow | `x = -sys.maxsize - 1` | Opposite overflow |
| **Float precision** | Floating point errors | `x = 0.1 + 0.2` | 0.30000000000000004 != 0.3 |
| **Infinity** | Infinite values | `x = float('inf')` | Math edge case |
| **NaN** | Not a number | `x = float('nan')` | NaN != NaN |

#### Example

**Function** (`src/math.py`):
```python
def calculate_discount(subtotal: float, discount_percent: int) -> float:
    """Calculate discounted price. Discount must be 0-100."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be 0-100")
    return subtotal * (1 - discount_percent / 100)
```

**Missing edge cases**:
- `discount_percent = 0` (no discount)
- `discount_percent = 100` (100% discount, result = 0)
- `discount_percent = -1` (below range, should raise)
- `discount_percent = 101` (above range, should raise)
- `subtotal = 0.0` (zero input)
- `subtotal = -10.0` (negative input)
- `subtotal = 0.1 + 0.2` (float precision: 99.99999...)

**Gap reported**:
```json
{
  "type": "gap",
  "category": "gap/missing-numeric-edge-cases",
  "file": "src/math.py",
  "function": "calculate_discount",
  "severity": "error",
  "edge_cases": [
    {
      "case": "zero discount",
      "description": "Discount of 0% should return full amount",
      "inputs": {"subtotal": 100.0, "discount_percent": 0},
      "expected": 100.0
    },
    {
      "case": "full discount",
      "description": "Discount of 100% should return zero",
      "inputs": {"subtotal": 100.0, "discount_percent": 100},
      "expected": 0.0
    },
    {
      "case": "negative discount",
      "description": "Negative discount should raise ValueError",
      "inputs": {"subtotal": 100.0, "discount_percent": -1},
      "expected": "ValueError"
    },
    {
      "case": "float precision",
      "description": "Float precision in calculation",
      "inputs": {"subtotal": 99.99, "discount_percent": 10},
      "expected": "~89.991 (allowing float tolerance)"
    }
  ]
}
```

### 2. Collection Edge Cases

**Category**: `gap/missing-collection-edge-cases`

Tests for empty, single, and large collections.

#### Common Cases

| Case | Example | Input | Note |
|------|---------|-------|------|
| **Empty** | Empty collection | `[]`, `""`, `{}` | Often forgotten |
| **Single item** | One element | `[1]` | Boundary of "many" |
| **Duplicates** | Repeated values | `[1, 1, 1]` | May break dedup logic |
| **Large input** | Many items | `[1] * 1000000` | Performance/memory |
| **Nested** | Complex structure | `[[1, 2], [3, 4]]` | Recursion edge case |
| **Mixed types** | Heterogeneous data | `[1, "a", None]` | Type assumptions |

#### Example

**Function** (`src/list_utils.py`):
```python
def truncate_list(items: List[str], max_length: int = 10) -> List[str]:
    """Return first max_length items"""
    return items[:max_length]
```

**Missing edge cases**:
- Empty list: `[]`
- Single item: `["hello"]`
- Length equals max_length: `["a", "b", "c"]` with `max_length=3`
- Length exceeds max_length: `[str(i) for i in range(100)]` with `max_length=10`
- max_length = 0: `truncate_list(["a"], 0)` → `[]`
- Negative max_length: `truncate_list(["a"], -1)` → `[]`

### 3. String Edge Cases

**Category**: `gap/missing-string-edge-cases`

Tests for empty strings, whitespace, Unicode, and special characters.

#### Common Cases

| Case | Example | Input | Note |
|------|---------|-------|------|
| **Empty** | Zero characters | `""` | Often breaks assumptions |
| **Whitespace** | Spaces/tabs/newlines | `" "`, `"\t"`, `"\n"` | May not strip correctly |
| **Unicode** | Non-ASCII characters | `"こんにちは"`, `"😀"` | Encoding issues |
| **Special chars** | Control characters | `"\x00"`, `"\x1f"` | SQL injection, XSS |
| **Very long** | Large strings | `"a" * 1000000` | Memory/performance |
| **Mixed case** | Uppercase/lowercase | `"HeLLo"` | Case-sensitivity bugs |

#### Example

**Function** (`src/string_utils.py`):
```python
def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string to max_length, respecting character boundaries"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
```

**Missing edge cases**:
- Empty string: `truncate_string("", 10)` → `""`
- String already fits: `truncate_string("hello", 10)` → `"hello"`
- Exact length: `truncate_string("12345", 5)` → `"12345"`
- Unicode truncation: `truncate_string("こんにちは", 2)` → respects char boundaries
- Emoji: `truncate_string("👨‍👩‍👧‍👦 family", 3)` → respects emoji boundaries
- Newlines: `truncate_string("line1\nline2", 10)` → preserves newline or removes it?

### 4. State & Lifecycle Edge Cases

**Category**: `gap/missing-state-edge-cases`

Tests for initialization, state transitions, and cleanup.

#### Common Cases

| Case | Example | Scenario | Note |
|------|---------|----------|------|
| **Uninitialized** | State not set | Access before init | Common bug |
| **Double init** | Init called twice | Idempotency | May leak resources |
| **Invalid transition** | Impossible state change | Bypass validation | State machine violation |
| **Cleanup failure** | Exception in teardown | Resource leak | Handled correctly? |
| **Concurrent access** | Multiple threads | Race conditions | Thread safety |
| **Reuse** | Object used multiple times | Resetting state | Proper cleanup? |

#### Example

**Class** (`src/database.py`):
```python
class DatabaseConnection:
    def __init__(self, host: str):
        self.host = host
        self.connected = False
    
    def connect(self):
        """Establish connection"""
        self._socket = socket.connect(self.host)
        self.connected = True
    
    def close(self):
        """Close connection"""
        if self.connected:
            self._socket.close()
            self.connected = False
```

**Missing edge cases**:
- `close()` before `connect()` (uninitialized state)
- `connect()` then `connect()` again (double initialization, socket leak)
- `connect()` fails → exception → `close()` called in finally (error handling)
- Multiple `close()` calls (idempotency)
- Exception during connect, socket not properly cleaned up

### 5. Resource & Performance Edge Cases

**Category**: `gap/missing-resource-edge-cases`

Tests for resource exhaustion and performance limits.

#### Common Cases

| Case | Example | Scenario | Note |
|------|---------|----------|------|
| **Resource exhaustion** | Out of memory | 1GB list allocation | OOM handling |
| **Timeout** | Long-running operation | Network call hangs | Timeout enforcement |
| **File handles** | Too many open files | 10000 files | Resource leak |
| **Connection pool** | Pool exhausted | All connections busy | Queueing/rejection |
| **Disk full** | Write to full disk | No space | Error handling |

#### Example

**Function** (`src/file_utils.py`):
```python
def read_large_file(path: str) -> str:
    """Read entire file into memory"""
    with open(path) as f:
        return f.read()
```

**Missing edge cases**:
- Very large file (1GB+) → Out of memory
- File deleted during read → FileNotFoundError
- Permission denied on read → PermissionError
- Partial read failure → Incomplete data

### 6. Error Path Edge Cases

**Category**: `gap/missing-error-edge-cases`

Tests for error conditions and recovery.

#### Common Cases

| Case | Example | Scenario | Note |
|------|---------|----------|------|
| **Missing file** | FileNotFoundError | Invalid path | Expected error |
| **Invalid format** | JSONDecodeError | Corrupted data | Parse error |
| **Network error** | ConnectionError | No connectivity | Timeout/disconnect |
| **Permission** | PermissionError | No access | Security boundary |
| **Type mismatch** | TypeError | Wrong type passed | Validation error |
| **Out of range** | IndexError | Invalid index | Boundary error |

#### Example

**Function** (`src/config.py`):
```python
def load_config(path: str) -> dict:
    """Load JSON config file"""
    with open(path) as f:
        return json.load(f)
```

**Missing error case tests**:
- File doesn't exist: `load_config("/nonexistent")` → `FileNotFoundError`
- Invalid JSON: `load_config("invalid.json")` → `JSONDecodeError`
- Empty file: `load_config("empty.json")` → Empty dict or error?
- Permission denied: `load_config("/root/secret.json")` → `PermissionError`

### 7. Type Coercion Edge Cases

**Category**: `gap/missing-type-coercion-edge-cases`

Tests for implicit type conversions and validation.

#### Common Cases

| Case | Example | Input | Note |
|------|---------|-------|------|
| **None** | Null value | `None` | Often crashes |
| **Wrong type** | Type mismatch | string instead of int | Implicit conversion? |
| **False-y values** | 0, empty string, False | `0`, `""`, `False` | Treated as falsy? |
| **Truthy values** | Non-empty values | `"hello"`, `[1]`, `1` | Treated as truthy? |

#### Example

**Function** (`src/validators.py`):
```python
def parse_count(value) -> int:
    """Parse count value"""
    return int(value)
```

**Missing edge cases**:
- `None` → `TypeError: int() argument must be a string...`
- `"abc"` → `ValueError: invalid literal for int()`
- `""` → `ValueError: invalid literal for int()`
- `"0"` → `0` (falsy int)
- `" 42 "` → `42` (whitespace handling)

## Edge Case Detection Algorithm

### 1. Function Analysis

```python
class EdgeCaseDetector:
    def analyze_function(func: FunctionInfo) -> List[EdgeCase]:
        """Analyze function for missing edge cases"""
        
        # Extract signature
        params = func.parameters
        return_type = func.return_type
        
        # Find parameter types
        edge_cases = []
        for param in params:
            param_type = param.annotation or infer_type(param)
            
            if param_type in (int, float):
                edge_cases.extend(get_numeric_cases(param_type))
            elif param_type in (list, tuple, set):
                edge_cases.extend(get_collection_cases(param_type))
            elif param_type == str:
                edge_cases.extend(get_string_cases())
            elif is_optional(param_type):
                edge_cases.append(EdgeCase("None input", param))
        
        return edge_cases
```

### 2. Test Coverage Check

For each edge case, check if it's covered by existing tests:

```python
def is_edge_case_covered(edge_case: EdgeCase) -> bool:
    """Check if edge case is tested"""
    
    for test in tests_covering(edge_case.function):
        test_inputs = extract_inputs(test)
        if matches_edge_case(test_inputs, edge_case):
            return True
    
    return False
```

### 3. Suggestion Generation

```python
def generate_test_suggestion(edge_case: EdgeCase) -> TestSuggestion:
    """Generate test suggestion for edge case"""
    
    return TestSuggestion(
        test_name=f"test_{function}_{edge_case.category}",
        description=edge_case.description,
        inputs=edge_case.inputs,
        expected=edge_case.expected,
        code_template=generate_template(edge_case)
    )
```

## Reporting

Edge cases appear in structured format:

```json
{
  "type": "gap",
  "category": "gap/missing-edge-cases",
  "file": "src/utils.py",
  "function": "calculate_discount",
  "severity": "warning",
  "message": "Missing edge case tests for numeric boundaries",
  "edge_cases": [
    {
      "type": "numeric",
      "scenario": "zero value",
      "description": "Discount of 0% should return full amount",
      "test_input": {"subtotal": 100.0, "discount_percent": 0},
      "expected": 100.0
    },
    {
      "type": "numeric",
      "scenario": "boundary value",
      "description": "Discount of 100% should return zero",
      "test_input": {"subtotal": 100.0, "discount_percent": 100},
      "expected": 0.0
    },
    {
      "type": "numeric",
      "scenario": "out of range",
      "description": "Negative discount should raise ValueError",
      "test_input": {"subtotal": 100.0, "discount_percent": -1},
      "expected": "ValueError"
    }
  ]
}
```

## Configuration

```json
{
  "edge_cases": {
    "enabled": true,
    "detection": {
      "numeric": true,
      "collections": true,
      "strings": true,
      "state": true,
      "resources": true,
      "errors": true,
      "type-coercion": true
    },
    "suggest-tests": true
  }
}
```

## See Also

- [GAP_DETECTION.md](./GAP_DETECTION.md) - Coverage gaps
- [RULES.md](./RULES.md) - Quality rules
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [LLM_AGENTS.md](./LLM_AGENTS.md) - Agent integration
