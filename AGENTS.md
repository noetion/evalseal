# Repository workflow

## Branch naming

Use `<type>/<short-description>` for working branches. Do not include an
author, username, agent, or tool name unless the repository owner explicitly
requests it.

Allowed work types:

- `feature` for new user-facing capability;
- `bugfix` for ordinary defect correction;
- `hotfix` for urgent correction of a released production defect;
- `release` for release preparation;
- `docs` for documentation-only work;
- `refactor` for behavior-preserving restructuring;
- `test` for test-only changes;
- `chore` for maintenance, release, or tooling work.

Choose the type that represents the primary purpose when a change spans categories. Use lowercase kebab-case for the description.
