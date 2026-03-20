---
name: commit
description: Git commit workflow using conventional commit messages. Use this when asked to make commits.
---

# Commit Changes Skill

## Overview

Create git commits for changes made during a session with user approval and no Claude attribution.

## Context

- You are tasked with creating meaningful git commits for all changes
- The user trusts your judgment on grouping related changes
- Commits must be authored solely by the user
- All changes should follow conventional commit message style

## Workflow

### Step 1: Review Changes

- Review the conversation history to understand what was accomplished
- Run `git status` to see current changes
- Run `git diff` to understand the modifications
- Determine if changes should be one commit or multiple logical commits

### Step 2: Plan Commits

- Identify which files belong together logically
- **Select the primary scope** by analyzing which component/area the changes affect most:
  - Extract the semantic component name (e.g., "cli", "analyzers", "config")
  - For multi-file changes in same component, use that component as scope
  - For changes spanning multiple components, pick the PRIMARY one and mention others in body
  - For infrastructure/config changes only, use `(tooling)` or `(config)` as appropriate
- Draft clear, descriptive commit messages using imperative mood
- Focus on why the changes were made, not just what
- Follow the Conventional Commit format with scope notation

### Step 3: Present Plan to User

- MUST: Always present the commit plan to the user before executing
- List the files you plan to add for each commit
- Show the commit message(s) you'll use
- MUST: Ask for confirmation: "I plan to create [N] commit(s) with these changes. Shall I proceed?"

### Step 4: Execute Upon Confirmation

- MUST: NEVER execute without user confirmation
- Use `git add` with specific files (never use `-A` or `.`)
- Create commits with the planned messages
- Show results with `git log --oneline -n [number]`

## Conventions

### Commit Message Format

```
<type>(<scope>): <subject>

<body>
```

### Type Prefixes

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `chore`: Other changes
- `refactor`: Code changes that neither fix a bug nor add a feature
- `test`: Adding or updating tests

### Scope Format

Scopes should represent the logical component or area being changed, not individual files.

#### Scope Generation Rules

1. **Analyze changed files** to identify the component area
2. **Use hierarchical naming** for nested components: `(parent/child)`
3. **Prefer semantic names** over file paths
4. **Single commit with multiple components**: Use the most relevant primary scope, mention secondary components in the body if needed
5. **Ignore infrastructure files**: Don't create scopes for config files (pyproject.toml, .gitignore) unless that's the primary change

#### Examples of valid scopes:

- `(analyzers)` - Changes to any analyzer module
- `(analyzers/code-review)` - Specific analyzer feature
- `(cli)` - CLI interface changes
- `(reporter)` - Output/reporting changes
- `(config)` - Configuration handling
- `(tooling)` - Development tooling setup
- `(docs)` - Documentation updates
- `(test)` - Testing infrastructure

#### Multi-component commits

When a commit affects multiple components, use the PRIMARY component as the scope and mention others in the body:

```
feat(cli): Add argument parsing for verbose mode

- Implement verbose flag handling
- Update reporter module for verbose output
- Add CLI tests for flag combinations
```

### Message Example

`feat(analyzers/code-review): Add new code review analyzer for Python`

## Important Constraints

- **User-only authorship**: Commits must be authored solely by the user
- **No attribution**: Do not include "Generated with Claude" messages
- **No co-authoring**: Do not add "Co-Authored-By" lines
- **Natural voice**: Write commit messages as if the user wrote them
- **Atomic commits**: Group related changes together; keep commits focused
- **Conventional style**: Always use the conventional commit format
