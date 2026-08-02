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

## Pull requests

Keep each pull request focused on one outcome. Its description should explain:

- what changed and why;
- how the change was verified;
- material risks or limitations;
- reviewer guidance; and
- follow-up work intentionally left out.

Add a pull-request comment when later verification, screenshots, release
evidence, or review context does not belong in the original description. Do not
leave reviewers to reconstruct important decisions from the commit history.
