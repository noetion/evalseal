# Changelog

All notable changes to EvalSeal are recorded here.

## [Unreleased]

## [0.1.0] - 2026-08-02

### Added

- Deterministic evidence-pack validation across 13 JSON schemas.
- Risk-scaled tailoring, governance authority, change-trigger, freshness,
  chronology, and exact-byte approval checks.
- `init`, `hash`, `assess-change`, `preflight`, and final `gate` commands.
- A non-approvable starter template and an end-to-end fictional example.
- Hash-locked Linux CPython 3.13 dependencies and protected workflow template.

### Changed

- Unified the repository, Python distribution, import package, installed
  command, wheel, documentation, and CI identifiers under the EvalSeal name.

### Security

- Final approvals bind the exact decision inputs and fail closed after any
  bound-file change.
- Text files use canonical LF bytes across platforms, while the wheel is treated
  as binary.
