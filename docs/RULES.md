# pytest-doctor: Diagnostic Rules

See [ARCHITECTURE.md](./ARCHITECTURE.md) for system overview.

pytest-doctor includes 40+ diagnostic rules across 7 categories to ensure high-quality test suites.

## Rule Categories

- [Structure Rules](#1-structure-rules) - Naming, organization, naming conventions
- [Assertion Rules](#2-assertion-rules) - Assertion quality and clarity
- [Fixture Rules](#3-fixture-rules) - Fixture best practices
- [Mocking Rules](#4-mocking-rules) - Mock and patch patterns
- [Performance Rules](#5-performance-rules) - Test speed and optimization
- [Maintainability Rules](#6-maintainability-rules) - Code clarity and duplication
- [Coverage Rules](#7-coverage-rules) - Code coverage metrics

## 1. Structure Rules

Rules for test file and function naming, organization, and documentation.

### `structure/test-file-naming`
**Severity**: `warning` | **Category**: Naming

Test files should follow naming convention: `test_*.py` or `*_test.py`

```python
# ✅ GOOD
tests/test_auth.py
tests/unit/test_user_service.py
auth_test.py

# ❌ BAD
tests/auth.py
tests/tests.py
test-auth.py  # underscore required
```

### `structure/test-class-naming`
**Severity**: `warning` | **Category**: Naming

Test classes should start with `Test` prefix.

```python
# ✅ GOOD
class TestUserService:
    def test_creates_user(self):
        pass

# ❌ BAD
class UserServiceTests:
    pass

class Helpers:
    pass
```

### `structure/test-function-naming`
**Severity**: `warning` | **Category**: Naming

Test functions should start with `test_` prefix.

```python
# ✅ GOOD
def test_user_creation():
    pass

def test_invalid_email_raises_error():
    pass

# ❌ BAD
def user_creation():
    pass

def check_valid_email():
    pass
```

### `structure/descriptive-test-names`
**Severity**: `info` | **Category**: Naming

Test names should clearly describe what they test.

```python
# ✅ GOOD
def test_calculate_discount_returns_zero_for_100_percent():
    pass

def test_send_email_raises_on_invalid_recipient():
    pass

# ❌ BAD
def test_discount():
    pass

def test_email():
    pass

def test_1():
    pass
```

### `structure/test-docstring`
**Severity**: `info` | **Category**: Documentation

Test functions should have docstrings explaining the test.

```python
# ✅ GOOD
def test_validate_email():
    """Verify valid emails are accepted"""
    assert validate_email("user@example.com")

# ❌ BAD
def test_validate_email():
    assert validate_email("user@example.com")
```

### `structure/test-class-organization`
**Severity**: `warning` | **Category**: Organization

Related tests should be grouped in classes.

```python
# ✅ GOOD
class TestUserCreation:
    def test_creates_with_valid_email(self):
        pass
    
    def test_raises_on_invalid_email(self):
        pass

# ❌ BAD
def test_user_creation_valid():
    pass

def test_user_creation_invalid():
    pass
```

### `structure/one-assertion-per-test`
**Severity**: `warning` | **Category**: Best Practice

Each test should verify one behavior (may have multiple assertions on same concept).

```python
# ✅ GOOD
def test_user_has_name_and_email():
    user = create_user("john", "john@example.com")
    assert user.name == "john"
    assert user.email == "john@example.com"

# ❌ BAD (multiple behaviors)
def test_user_creation_and_saving():
    user = create_user("john", "john@example.com")
    assert user.name == "john"
    save_user(user)
    assert user.id is not None
```

### `structure/arrange-act-assert`
**Severity**: `info` | **Category**: Pattern

Follow Arrange-Act-Assert pattern: setup → execute → verify.

```python
# ✅ GOOD
def test_calculate_discount():
    # Arrange
    subtotal = 100.0
    discount = 10
    
    # Act
    result = calculate_discount(subtotal, discount)
    
    # Assert
    assert result == 90.0
```

## 2. Assertion Rules

Rules for assertion quality, clarity, and correctness.

### `assertions/missing-assertion-message`
**Severity**: `warning` | **Category**: Clarity

Assertions should include messages for debugging.

```python
# ✅ GOOD
assert token is not None, "Token should not be None after login"
assert len(users) == 1, f"Expected 1 user, got {len(users)}"

# ❌ BAD
assert token is not None
assert len(users) == 1
```

### `assertions/no-bare-asserts`
**Severity**: `warning` | **Category**: Style

Use specific assertion methods, not bare `assert`.

```python
# ✅ GOOD (pytest style)
assert user.name == "john"  # implicit equality check
assert user is not None

# ⚠️ ACCEPTABLE
self.assertEqual(user.name, "john")  # unittest style

# ❌ BAD
assert(user.name == "john")  # looks like function call
```

### `assertions/multiple-assertions-per-test`
**Severity**: `warning` | **Category**: Best Practice

Tests should focus on one behavior (multiple assertions on same topic OK).

```python
# ✅ GOOD
def test_user_fields():
    user = create_user("john", "john@example.com", age=30)
    assert user.name == "john"
    assert user.email == "john@example.com"
    assert user.age == 30

# ❌ BAD (testing multiple behaviors)
def test_user_creation():
    user = create_user("john", "john@example.com")
    assert user.name == "john"
    assert user.id is not None
    assert send_welcome_email(user)
    assert user in get_all_users()
```

### `assertions/float-comparison-equality`
**Severity**: `error` | **Category**: Correctness

Use `pytest.approx()` for float equality.

```python
# ✅ GOOD
assert result == pytest.approx(3.14159)
assert result == pytest.approx(expected, rel=1e-5)

# ❌ BAD
assert result == 3.14159  # Float precision issues
assert abs(result - expected) < 0.001  # Old way
```

### `assertions/type-checking-in-assertions`
**Severity**: `info` | **Category**: Style

Use `isinstance()` for type checks, not `type()`.

```python
# ✅ GOOD
assert isinstance(user, User)
assert isinstance(count, int)

# ❌ BAD
assert type(user) == User  # Breaks with subclasses
assert type(count) is int
```

### `assertions/unreachable-assertions`
**Severity**: `error` | **Category**: Correctness

Assertions after early return or exceptions are unreachable.

```python
# ❌ BAD
def test_user():
    user = get_user()
    assert user is not None
    # Following lines never execute if assertion fails
    assert user.email is not None
```

## 3. Fixture Rules

Rules for proper fixture usage, scope, and dependencies.

### `fixtures/unused-fixtures`
**Severity**: `warning` | **Category**: Code Quality

Declared fixtures should be used in at least one test.

```python
# ✅ GOOD
@pytest.fixture
def user():
    return User(name="john")

def test_user_name(user):  # fixture is used
    assert user.name == "john"

# ❌ BAD
@pytest.fixture
def unused_data():  # never used
    return {"key": "value"}
```

### `fixtures/incorrect-fixture-scope`
**Severity**: `warning` | **Category**: Performance

Fixture scope should match usage pattern.

```python
# ✅ GOOD
@pytest.fixture(scope="function")  # reset per test
def temp_database():
    db = create_db()
    yield db
    db.cleanup()

# ❌ BAD (stale data across tests)
@pytest.fixture(scope="session")
def temp_database():
    db = create_db()
    return db  # persists across all tests
```

### `fixtures/complex-fixture-dependencies`
**Severity**: `info` | **Category**: Maintainability

Fixture dependency chains should not exceed 3 levels.

```python
# ✅ GOOD
@pytest.fixture
def user(db):
    return db.create_user()

# ❌ BAD (4+ levels)
@pytest.fixture
def a(b): pass
@pytest.fixture
def b(c): pass
@pytest.fixture
def c(d): pass
@pytest.fixture
def d(e): pass
@pytest.fixture
def e(): pass
```

### `fixtures/mutable-fixture-returns`
**Severity**: `error` | **Category**: Correctness

Fixtures returning mutable objects may cause test pollution.

```python
# ✅ GOOD
@pytest.fixture
def user_data():
    return {"name": "john"}  # fresh copy each test

@pytest.fixture
def config():
    return dataclasses.replace(DEFAULT_CONFIG)  # copy

# ❌ BAD (shared mutable state)
DEFAULT_USER = {"name": "john"}

@pytest.fixture
def user():
    return DEFAULT_USER  # shared across tests
```

### `fixtures/setup-teardown-usage`
**Severity**: `warning` | **Category**: Style

Use fixtures instead of old `setup()`/`teardown()` methods.

```python
# ✅ GOOD
@pytest.fixture
def database():
    db = setup_db()
    yield db
    teardown_db(db)

# ⚠️ ACCEPTABLE
class TestDatabase:
    def setup_method(self):
        self.db = setup_db()
    
    def teardown_method(self):
        self.db.close()

# ❌ BAD
def setUp(self):  # wrong method name
    pass
```

## 4. Mocking Rules

Rules for proper mocking and patching patterns.

### `mocking/mock-without-spec`
**Severity**: `warning` | **Category**: Best Practice

Mocks should use `spec` to prevent calling non-existent methods.

```python
# ✅ GOOD
mock_user = Mock(spec=User)
mock_service = Mock(spec=UserService)

# ❌ BAD (accepts any attribute/method)
mock_user = Mock()
mock_user.nonexistent_method()  # no error caught
```

### `mocking/patch-wrong-import-path`
**Severity**: `error` | **Category**: Correctness

Patch the location where object is used, not where it's defined.

```python
# ✅ GOOD
# In auth.py: from api import get_user
@patch('auth.get_user')  # patch where imported
def test_login(mock_get_user):
    pass

# ❌ BAD
@patch('api.get_user')  # patches original location
def test_login(mock_get_user):
    pass
```

### `mocking/unmocked-external-calls`
**Severity**: `error` | **Category**: Best Practice

External calls (network, database) should be mocked.

```python
# ✅ GOOD
@patch('requests.get')
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    result = fetch_user(1)
    assert result["id"] == 1

# ❌ BAD (makes real network call)
def test_fetch_user():
    result = fetch_user(1)  # real HTTP request
    assert result["id"] == 1
```

### `mocking/side-effect-vs-return-value`
**Severity**: `info` | **Category**: Clarity

Use appropriate mock configuration.

```python
# ✅ GOOD
mock.return_value = 42  # for normal return
mock.side_effect = ValueError("invalid")  # for exceptions
mock.side_effect = [1, 2, 3]  # for multiple calls

# ❌ BAD
mock.return_value = [ValueError("invalid")]  # wrong pattern
```

### `mocking/mock-assertion-counts`
**Severity**: `info` | **Category**: Clarity

Verify mocks are called expected number of times.

```python
# ✅ GOOD
mock_save.assert_called_once()
mock_save.assert_called_once_with(user)
mock_delete.assert_not_called()
mock_update.assert_called()

# ❌ BAD (no verification)
mock_save(user)
# no assertion that mock_save was called
```

## 5. Performance Rules

Rules for test speed and efficiency.

### `performance/slow-tests`
**Severity**: `warning` | **Category**: Performance

Tests should complete quickly (target: <1s per test).

```
⚠️ test_database_sync_all_users: 5.2s (slow)
⚠️ test_email_integration: 3.8s (slow)
⚠️ test_api_call_chain: 2.1s (slow)
```

### `performance/missing-parametrization`
**Severity**: `info` | **Category**: Best Practice

Repeated test logic should use `@pytest.mark.parametrize`.

```python
# ✅ GOOD
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_validate_email(email, valid):
    assert validate_email(email) == valid

# ❌ BAD (duplicated logic)
def test_validate_email_valid():
    assert validate_email("user@example.com")

def test_validate_email_invalid():
    assert not validate_email("invalid-email")

def test_validate_email_empty():
    assert not validate_email("")
```

### `performance/expensive-setup`
**Severity**: `warning` | **Category**: Performance

Heavy setup should not run for lightweight tests.

```python
# ✅ GOOD
@pytest.fixture(scope="session")
def database():
    # expensive setup shared across tests
    return setup_database()

# ❌ BAD
@pytest.fixture(scope="function")
def database():
    # expensive setup for each test
    return setup_database()
```

## 6. Maintainability Rules

Rules for code clarity, duplication, and test independence.

### `maintainability/magic-numbers-in-tests`
**Severity**: `info` | **Category**: Clarity

Hard-coded values should use named constants.

```python
# ✅ GOOD
MAX_RETRIES = 3
TIMEOUT_MS = 5000

def test_retry_logic():
    result = retry(operation, max_retries=MAX_RETRIES)
    assert result is not None

# ❌ BAD
def test_retry_logic():
    result = retry(operation, max_retries=3)
    assert result is not None
```

### `maintainability/duplicate-test-code`
**Severity**: `warning` | **Category**: DRY

Duplicated test setup should be extracted to fixtures.

```python
# ✅ GOOD
@pytest.fixture
def authenticated_user():
    return create_user_and_login()

def test_profile_update(authenticated_user):
    authenticated_user.update_profile(name="Jane")
    assert authenticated_user.name == "Jane"

# ❌ BAD
def test_profile_update():
    user = create_user_and_login()
    user.update_profile(name="Jane")
    assert user.name == "Jane"

def test_profile_delete():
    user = create_user_and_login()  # duplicated
    user.delete_profile()
    assert not user.has_profile()
```

### `maintainability/missing-error-cases`
**Severity**: `error` | **Category**: Coverage

Functions should have tests for error/failure paths.

See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap detection.

### `maintainability/test-interdependence`
**Severity**: `error` | **Category**: Correctness

Tests should not depend on execution order.

```python
# ✅ GOOD (independent tests)
def test_user_creation():
    user = create_user("john")
    assert user.id is not None

def test_user_listing():
    users = get_all_users()
    assert isinstance(users, list)

# ❌ BAD (dependent)
def test_create_user():
    global created_user
    created_user = create_user("john")

def test_list_users():
    users = get_all_users()
    assert created_user in users  # depends on previous test
```

### `maintainability/descriptive-assertions`
**Severity**: `info` | **Category**: Clarity

See [assertions/missing-assertion-message](#assertionsmissing-assertion-message)

## 7. Coverage Rules

Rules for code coverage metrics.

### `coverage/low-coverage`
**Severity**: `warning` | **Category**: Coverage

Overall test coverage should meet minimum threshold (default: 80%).

```
⚠️ Overall coverage: 62% (below 80% minimum)
```

### `coverage/uncovered-function`
**Severity**: `error` | **Category**: Coverage

See [GAP_DETECTION.md#1-untested-functions](./GAP_DETECTION.md#1-untested-functions)

### `coverage/uncovered-branch`
**Severity**: `error` | **Category**: Coverage

See [GAP_DETECTION.md#2-uncovered-branches](./GAP_DETECTION.md#2-uncovered-branches)

### `coverage/partial-function-coverage`
**Severity**: `warning` | **Category**: Coverage

See [GAP_DETECTION.md#6-partial-function-coverage](./GAP_DETECTION.md#6-partial-function-coverage)

## Rule Configuration

Rules can be configured in `pytest_doctor.config.json`:

```json
{
  "rules": {
    "structure/test-file-naming": {
      "enabled": true,
      "severity": "warning"
    },
    "assertions/multiple-assertions-per-test": {
      "enabled": true,
      "severity": "info",
      "max_assertions": 5
    }
  },
  "ignore": {
    "rules": [
      "performance/slow-tests",
      "structure/descriptive-test-names"
    ]
  }
}
```

## Severity Levels

- **error** (🔴): Critical issue that may cause test failures or bugs
- **warning** (🟡): Important best practice violation
- **info** (ℹ️): Nice-to-have improvement for clarity

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Quick start
- [SCORING.md](./SCORING.md) - How rules affect score
- [GAP_DETECTION.md](./GAP_DETECTION.md) - Coverage gaps
- [EDGE_CASES.md](./EDGE_CASES.md) - Missing edge cases
- [CONFIG.md](./CONFIG.md) - Configuration options
