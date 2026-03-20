# pytest-doctor: LLM Agent Integration

See [OVERVIEW.md](./OVERVIEW.md) for overview.

pytest-doctor is designed for LLM coding agents (Claude, Cursor, OpenCode, etc.) to generate and improve tests.

## How Agents Use pytest-doctor

### 1. Analysis Phase

Agent analyzes test suite to identify gaps and issues:

```python
from pytest_doctor import diagnose

# Get comprehensive analysis
result = diagnose("./tests")

# Identify what needs work
gaps = result.gaps
quality_issues = [d for d in result.diagnostics 
                  if d.severity == "error"]
coverage = result.coverage.overall
```

### 2. Interpretation Phase

Agent understands the diagnostics:

```
Gaps Found:
- Untested function: src/auth.py::validate_token
- Missing exception test: TokenExpiredException
- Missing edge cases: empty string, None input

Quality Issues:
- Missing assertion messages (8 violations)
- Unused fixtures (2 violations)

Coverage:
- Overall: 72%
- auth.py: 45% (low)
- database.py: 95% (good)
```

### 3. Generation Phase

Agent generates missing tests based on structured suggestions:

```python
# Agent receives structured test suggestion
gap = result.gaps[0]

test_suggestion = gap.test_suggestion
# {
#   "test_name": "test_validate_token_raises_on_expired",
#   "description": "Verify TokenExpiredException on expired token",
#   "inputs": {"token": "expired_jwt_token"},
#   "expected": "Raises TokenExpiredException"
# }

# Agent generates test
test_code = f"""
def {test_suggestion.test_name}():
    \"{test_suggestion.description}\"
    token = jwt.encode({{}}, SECRET, algorithm="HS256")
    # Simulate expiration
    with travel_to(datetime.now() + timedelta(days=1)):
        with pytest.raises(TokenExpiredException):
            validate_token(token)
"""
```

### 4. Verification Phase

Agent rescans to verify improvement:

```python
# Write test
write_test(test_code)

# Re-analyze
new_result = diagnose("./tests")

# Check if improved
if len(new_result.gaps) < len(result.gaps):
    print("✅ Gap fixed!")
else:
    print("⚠️ Gap still exists")
```

## Structured Output for Agents

### Gap Diagnostics

Each gap includes structured information for agents:

```json
{
  "type": "gap",
  "category": "gap/missing-exception-tests",
  "severity": "error",
  "file": "src/auth.py",
  "function": "validate_token",
  "line": 45,
  "message": "TokenExpiredException is raised but never tested",
  "help": "The function raises TokenExpiredException when token is expired, but no test verifies this behavior",
  
  "test_suggestion": {
    "test_name": "test_validate_token_raises_on_expired",
    "test_pattern": "exception",
    "description": "Verify TokenExpiredException is raised for expired tokens",
    "inputs": {
      "token": "expired_jwt_token",
      "current_time": "after_token_expiration"
    },
    "expected": "Raises TokenExpiredException with message containing 'expired'",
    "code_template": "with pytest.raises(TokenExpiredException):\n    validate_token(expired_token)"
  }
}
```

### Edge Case Suggestions

Each edge case includes test generation hints:

```json
{
  "type": "gap",
  "category": "gap/missing-edge-cases",
  "function": "truncate_string",
  "severity": "warning",
  "edge_cases": [
    {
      "scenario": "empty string",
      "description": "Empty string should return empty string",
      "test_input": {"text": "", "max_length": 10},
      "expected": "",
      "test_name": "test_truncate_string_empty_input"
    },
    {
      "scenario": "unicode characters",
      "description": "Should respect character boundaries for Unicode",
      "test_input": {"text": "こんにちは", "max_length": 2},
      "expected": "こん",
      "test_name": "test_truncate_string_unicode_boundary"
    }
  ]
}
```

### Quality Issues

Structured format for agent interpretation:

```json
{
  "type": "quality",
  "category": "assertions/missing-messages",
  "severity": "warning",
  "file": "tests/test_auth.py",
  "line": 25,
  "message": "Assertion lacks message for debugging",
  "help": "When assertions fail, a message helps explain what went wrong",
  "code": "assert token is not None",
  "suggestion": "assert token is not None, 'Token should not be None after login'"
}
```

## Agent Workflows

### Workflow 1: Fix All Gaps

```python
from pytest_doctor import diagnose

def fix_test_gaps():
    # Step 1: Analyze
    result = diagnose("./tests")
    
    # Step 2: For each gap, generate test
    for gap in result.gaps:
        if gap.test_suggestion:
            # Generate from suggestion
            test_code = agent.generate_test(gap.test_suggestion)
            
            # Write test
            test_file = determine_test_file(gap)
            append_test(test_file, test_code)
    
    # Step 3: Verify improvements
    new_result = diagnose("./tests")
    print(f"Gaps reduced: {len(result.gaps)} → {len(new_result.gaps)}")
    print(f"Score improved: {result.score.value} → {new_result.score.value}")
```

### Workflow 2: Improve Coverage

```python
def improve_coverage(target: int = 90):
    result = diagnose("./tests")
    
    while result.coverage.overall < target:
        # Find lowest coverage file
        low_file = min(
            result.coverage.by_file.items(),
            key=lambda x: x[1]
        )[0]
        
        # Generate tests for uncovered code
        uncovered = find_uncovered_lines(low_file)
        
        for line in uncovered[:5]:  # Fix 5 at a time
            func = find_function_at_line(line)
            test = agent.generate_test_for_function(func)
            write_test(test)
        
        # Re-check
        result = diagnose("./tests")
        print(f"Coverage: {result.coverage.overall}%")
```

### Workflow 3: Fix Quality Issues

```python
def fix_quality_issues():
    result = diagnose("./tests")
    
    # Group by category
    issues_by_category = group_by(result.diagnostics, "category")
    
    for category, issues in issues_by_category.items():
        if len(issues) > 5:
            # Ask agent to fix pattern
            fix_code = agent.fix_pattern(category, issues[0])
            
            # Apply fix to all similar issues
            for issue in issues:
                apply_fix(issue, fix_code)
    
    # Verify
    new_result = diagnose("./tests")
    print(f"Quality issues fixed: {len(result.diagnostics)} → {len(new_result.diagnostics)}")
```

### Workflow 4: Iterative Improvement

```python
def iterative_improvement(max_iterations: int = 10):
    result = diagnose("./tests")
    iteration = 0
    
    while result.score.value < 90 and iteration < max_iterations:
        iteration += 1
        
        # Get top issue
        top_issue = result.diagnostics[0]
        
        # Show agent the issue
        print(f"\nIteration {iteration}: {top_issue.category}")
        print(f"Current score: {result.score.value}")
        
        # Agent fixes it
        solution = agent.fix_issue(top_issue)
        apply_solution(solution)
        
        # Re-analyze
        result = diagnose("./tests")
    
    print(f"✅ Final score: {result.score.value}")
```

## Agent Integration Examples

### Claude (via API)

```python
from pytest_doctor import diagnose
import anthropic

def improve_tests_with_claude():
    # Analyze
    result = diagnose("./tests")
    
    # Create prompt for Claude
    prompt = f"""
    The test suite analysis shows these gaps:
    
    {format_gaps(result.gaps)}
    
    Coverage: {result.coverage.overall}%
    Score: {result.score.value}/100
    
    Please generate Python pytest code to:
    1. Fill the identified gaps
    2. Add missing edge case tests
    3. Improve coverage to at least 85%
    """
    
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract code from response
    test_code = extract_code_block(message.content[0].text)
    
    # Write tests
    write_test_file("tests/generated_tests.py", test_code)
    
    # Verify
    new_result = diagnose("./tests")
    return new_result.score.value
```

### Cursor (IDE Integration)

```python
# In .cursorrules or context
@pytest_doctor_analyzer
def analyze_tests():
    """
    Analyze test suite and suggest improvements.
    Use pytest-doctor to identify gaps and edge cases.
    
    When user asks to improve tests:
    1. Run: from pytest_doctor import diagnose
    2. Get gaps: result = diagnose("./tests")
    3. Generate: use gap.test_suggestion for test code
    4. Verify: re-run diagnose() to confirm improvement
    """
    
@pytest_doctor_generator
def generate_missing_tests(gap):
    """
    Generate test code for a specific gap.
    Use the test_suggestion field as template.
    """
```

### OpenCode Skill

```yaml
# pytest-doctor.yaml (OpenCode skill)
name: pytest-doctor
description: Analyze and improve Python test suites

commands:
  - name: analyze
    description: Analyze test suite for gaps and quality issues
    action: |
      from pytest_doctor import diagnose
      result = diagnose("./tests")
      return result
  
  - name: generate-tests
    description: Generate tests for identified gaps
    action: |
      from pytest_doctor import diagnose
      result = diagnose("./tests")
      
      for gap in result.gaps:
        if gap.test_suggestion:
          test_code = generate_from_template(gap.test_suggestion)
          write_test(test_code)
  
  - name: improve-coverage
    description: Improve test coverage to target percentage
    parameters:
      - name: target
        type: int
        default: 85
        description: Target coverage percentage
    action: |
      from pytest_doctor import diagnose
      result = diagnose("./tests")
      
      while result.coverage.overall < target:
        # Generate tests for uncovered code
        ...
```

## Structured Prompt Template for Agents

```
You are a Python test improvement specialist. 

Your task is to improve the test suite based on automated analysis.

## Current Analysis
{formatted_analysis_results}

## Your Task
1. Review the identified gaps and quality issues
2. Generate test code using the provided suggestions
3. Ensure new tests follow pytest best practices
4. Maintain consistency with existing test style

## Gaps to Address
{formatted_gaps_for_agent}

## Quality Guidelines
- Use descriptive test names (test_<function>_<scenario>)
- Include assertion messages
- Group related tests in classes
- Use fixtures for common setup
- Mock external dependencies

## Verification
After writing tests, the suite will be re-analyzed to verify:
- Score improvement
- Gap reduction
- Coverage increase

Please generate the test code now.
```

## Best Practices for Agents

### 1. Trust the Suggestions

Use the structured suggestions from pytest-doctor:

```python
# Good: Use provided suggestion
suggestion = gap.test_suggestion
test_name = suggestion.test_name
test_inputs = suggestion.inputs
expected = suggestion.expected

# Avoid: Making up test cases
# The suggestions are based on code analysis
```

### 2. Verify Improvements

Always re-run analysis after making changes:

```python
# Before
before = diagnose("./tests")

# Make changes
write_tests(...)

# After - verify improvement
after = diagnose("./tests")

if after.score.value > before.score.value:
    print("✅ Improvement verified")
else:
    print("⚠️ Unexpected - recheck implementation")
```

### 3. Fix Suggestions First

Address test suggestions in priority order:

```python
# Sort by severity
errors = [d for d in result.diagnostics 
          if d.severity == "error"]
warnings = [d for d in result.diagnostics 
            if d.severity == "warning"]

# Fix errors first (higher impact)
for error in errors:
    fix_issue(error)

# Then warnings
for warning in warnings:
    fix_issue(warning)
```

### 4. Handle Edge Cases

Use the edge case detector output:

```python
# If gap includes edge cases
for edge_case in gap.edge_cases:
    # Generate test from edge case description
    test = agent.generate_test_for_edge_case(edge_case)
    write_test(test)
```

### 5. Respect Configuration

Honor user's pytest-doctor configuration:

```python
# Load config
config = load_config("pytest_doctor.config.json")

# Don't generate tests for ignored files
for gap in result.gaps:
    if gap.location.file not in config.ignore.files:
        generate_test(gap)
```

## Monitoring Agent Progress

```python
def track_improvement(initial_result, final_result):
    """Track what agent improved"""
    
    metrics = {
        "score_improvement": final_result.score.value - initial_result.score.value,
        "gaps_fixed": len(initial_result.gaps) - len(final_result.gaps),
        "coverage_improvement": final_result.coverage.overall - initial_result.coverage.overall,
        "quality_issues_fixed": len(initial_result.diagnostics) - len(final_result.diagnostics),
    }
    
    print("Agent Improvements:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:+.1f}")
```

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Overview
- [API.md](./API.md) - Python API details
- [GAP_DETECTION.md](./GAP_DETECTION.md) - Gap detection details
- [EDGE_CASES.md](./EDGE_CASES.md) - Edge case categories
- [RULES.md](./RULES.md) - All diagnostic rules
