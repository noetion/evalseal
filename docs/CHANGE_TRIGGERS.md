# Change-trigger guide

Approval belongs to an exact system version. `config/change-triggers.reference.json` defines the minimum response when that version changes.

| Change family | Reference minimum |
|---|---|
| Documentation with no behavioral or governance effect | Documentation review |
| Prompt, refusal, routing, or policy text | Targeted evaluation and security reassessment |
| Model, provider, model snapshot, router, or grader | Full reassessment |
| Retrieval, embeddings, ranking, corpus, or ingestion | Targeted reassessment, expanded when data or authorization changes |
| Tool, permission, identity, approval, or egress | Full reassessment |
| Guardrail, parser, schema, renderer, or downstream interpreter | Targeted evaluation and security reassessment |
| Data class, retention, transfer, or privacy control | Full privacy, security, and legal reassessment |
| Purpose, affected population, autonomy, sector, or jurisdiction | Full reassessment |
| Material dependency, hosting, identity, or network change | Targeted security and operational reassessment |
| Monitoring, logging, rollback, containment, or incident process | Targeted operational reassessment |
| Material incident or prohibited event | Incident response plus reassessment and independent review |
| Drift, provider update, evidence expiry, or accumulated change | Full reassessment |

The machine-readable policy is authoritative for the gate. If several changes apply, the gate combines all required evidence and uses the broadest minimum scope.

Unknown change types fail closed. Add a reviewed policy trigger rather than describing a material change as `documentation_only`.

The change record is an accountable declaration, not an automatic diff against the prior baseline. Teams must use protected build metadata, configuration comparison, provider notices, and change review to identify every applicable type. The final gate requires a fresh approval for every candidate, including documentation-only releases; the trigger only changes reassessment scope and evidence requirements.
