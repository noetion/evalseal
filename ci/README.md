# CI reference

Vendor the complete, versioned release at `.governance/evaluation-methodology/`, including `dist/` and `RELEASE_MANIFEST.sha256`. Protect that directory and the copied workflow with CODEOWNERS or equivalent rules that candidate authors cannot satisfy alone. Copy `github-actions.yml` into `.github/workflows/` and call it from the protected deployment workflow with organization-specific evidence and policy paths.

The workflow does not install the adopting application as the gate. It verifies the vendored release manifest, installs the release wheel, and installs CPython 3.13 Linux dependencies from a hash-locked file. Its action dependencies are pinned to full official release commit SHAs, and workflow inputs pass through quoted environment variables rather than shell interpolation.

Configure an `evaluation-governance` GitHub environment with the required production reviewers. Make deployment depend on this job and run only the protected default-branch version of the workflow. If a central governance repository hosts the workflow instead, invoke it at an immutable full commit SHA.

The reference intentionally does not pass `--allow-conditional`. A conditional decision therefore stops automatic deployment unless the organization deliberately changes that policy.

Protect the vendored gate, called workflow, policy files, approval record, and deployment environment with the organization's required reviewers and identity controls. A wheel or workflow copied into an unprotected candidate-owned path is not a trustworthy gate.

## Release manifest maintenance

The manifest binds staged Git blobs, not platform-dependent working-tree bytes. After changing the protected release, stage every intended file, run `python scripts/generate_release_manifest.py`, stage `RELEASE_MANIFEST.sha256`, and run `python scripts/generate_release_manifest.py --check`. The repository's `.gitattributes` stores text as LF and treats wheels as binary.
