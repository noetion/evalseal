# Architecture and trust boundary

## Why this implementation exists

Current alternatives cover important parts of the workflow:

- [NIST OSCAL](https://pages.nist.gov/OSCAL/) provides standardized machine-readable formats for control implementation and assessment information.
- [Promptfoo](https://www.promptfoo.dev/docs/integrations/ci-cd/) and [DeepEval](https://deepeval.com/docs/introduction) execute LLM evaluations and can participate in CI/CD quality gates.
- Managed governance platforms such as [IBM watsonx.governance](https://www.ibm.com/docs/en/watsonx/w-and-w/2.3.x?topic=components-model-risk-governance-workflows) provide inventory and approval workflows.

This repository does not replace those systems. Its narrower job is to provide a portable, vendor-neutral contract that connects the methodology's LLM-specific evidence, change scope, governance authority, and final release decision. Evaluation tools can produce evidence artifacts; enterprise governance systems can become the protected source of policies and approval records.

Future OSCAL export or import can be added when an actual consumer requires it. The current schema stays smaller because an unused interoperability layer would add complexity without strengthening today's decision.

## Trust boundary

The gate establishes structural and referential consistency. It can prove that the bytes it checked match the recorded hashes and that the recorded evidence satisfies the configured rules. The approval record binds the exact pack and decision-input bytes; the gate report records the approval, policy, input, and gate-source digests plus its mode and deployment authority.

It cannot prove:

- that a human-readable report tells the truth;
- that a test harness exercised the intended production-equivalent system;
- that an actor identity was authenticated outside the file;
- that the configured policy is legally sufficient;
- that a model will never fail after approval; or
- that the deployment used the approved bytes.

Production assurance therefore depends on protected evidence generation, authenticated approvals, repository and CI integrity, deployment provenance, monitoring, and incident response around this gate. Production CI must install a manifest-verified, protected release of the gate rather than executing candidate-controlled gate code. The reference workflow uses a vendored release, hash-locked Linux dependencies, fully pinned official action commits, quoted environment inputs, and a protected governance environment.
