# Agent review instructions — Retroverse

Before proposing edits or reviewing a pull request:
1. Identify which Retroverse application or deployment the change targets. This repository includes historical and experimental routes; do not assume it is the live retroverse.live runtime.
2. Confirm the task's requested scope and compare each changed file against it.
3. Flag unrelated visual or navigation changes, especially additions to a minimal public homepage where applicable.
4. Flag changes to VirtualDJ bridge, publishing, Redis, indexing, media matching, secrets, network permissions, or paid API behavior unless explicitly authorized.
5. Check for broken mobile behavior, altered routes, extra fetching, and unnecessary dependencies.
6. Run or inspect relevant available tests and lint/build results. Never infer success from a PR description alone.
7. Report actionable findings with precise file references; distinguish proven defects from hypotheses.
8. Do not merge, deploy, delete, purchase, or initiate billed external services without explicit approval.

Review output: summary, affected scope, findings by severity, actual checks observed, risks, and approval recommendation.
