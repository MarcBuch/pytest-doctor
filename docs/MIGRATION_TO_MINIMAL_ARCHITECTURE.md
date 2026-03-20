# Migration Guide: Legacy -> Minimal Architecture

This guide maps the original analyzer-heavy design to the simplified, tool-reuse architecture.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the target state.

## Why Migrate

- Less custom analyzer maintenance
- Faster iteration by upgrading mature dependencies
- More predictable diagnostics across environments
- Cleaner API and configuration surface

## Concept Mapping

| Legacy Concept | Minimal Architecture Equivalent |
|---|---|
| `CodeAnalyzer` + `TestAnalyzer` custom AST logic | `ruff` diagnostics + optional pytest-style lint checks |
| Custom `CoverageEngine` logic | `coverage` / `pytest-cov` outputs normalized |
| Custom `GapDetector` | Coverage-derived gap diagnostics (`gap/*`) |
| Custom `EdgeCaseDetector` | Optional heuristic suggestions attached to diagnostics |
| `TestQualityAnalyzer` | `ruff` + pytest-oriented lint categories |
| Multiple internal analyzer result models | Unified `Diagnostic` model |
| Analyzer-specific scoring pieces | Severity + category weighted scoring |

## CLI Mapping

| Legacy Flag | New/Preferred Flag |
|---|---|
| `--no-rules` | `--no-lint` |
| `--no-gaps` | `--no-coverage` (if gaps derive from coverage pass) |
| `--no-coverage` | `--no-coverage` (unchanged) |
| N/A | `--no-dead-code` |
| N/A | `--no-complexity` |

## Configuration Mapping

| Legacy Key | Minimal Key |
|---|---|
| `gaps.enabled` | `coverage` (pass toggle) |
| `rules.*` large tree | `ignore.rules` + underlying tool config |
| deep scoring/gap penalty trees | compact `scoring.severity_weights` and `scoring.category_multipliers` |
| many nested analyzer options | `tools.<name>` optional overrides |

Example migration:

```json
{
  "coverage": { "enabled": true },
  "gaps": { "enabled": true },
  "rules": {
    "assertions/multiple-assertions-per-test": { "enabled": false }
  }
}
```

to:

```json
{
  "lint": true,
  "coverage": true,
  "deadCode": true,
  "complexity": true,
  "ignore": {
    "rules": ["pytest-style/multiple-assertions"]
  }
}
```

## API Mapping

| Legacy Usage | Minimal Usage |
|---|---|
| Iterate `result.gaps` as primary signal | Iterate `result.diagnostics` as primary signal |
| Distinct analyzer outputs | Unified diagnostic categories (`quality`, `gap`, `dead-code`, `complexity`, `coverage`) |
| Score breakdown with `coverage/quality/gaps` only | Score breakdown includes `dead_code` and `complexity` as needed |

## Recommended Migration Plan

1. Keep public `diagnose()` signature stable.
2. Make `diagnostics` the canonical API output in docs and examples.
3. Add adapter layer for tool output normalization.
4. Introduce pass toggles and mark old flags deprecated.
5. Keep compatibility shims for one release cycle.

## Backward Compatibility Strategy

- Preserve `result.gaps` as a derived subset of `result.diagnostics`.
- Accept old config keys with deprecation warnings and map them internally.
- Document deprecations in release notes and migration examples.

## Verification Checklist

- Same project produces stable score trend before/after migration
- JSON schema remains consumable by agent workflows
- CI gates still fail correctly on low score
- Ignore rules/files continue to suppress expected diagnostics

## See Also

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [API.md](./API.md)
- [CONFIG.md](./CONFIG.md)
- [SCORING.md](./SCORING.md)
