# Agent-eval runbook — running the pack against a live agent

The five fixtures in this directory are eval inputs with machine-gradable
properties. A structural pass proves they are well-formed; only a live run
proves anything about agent behavior. This runbook standardizes that run.

## Procedure

1. Confirm the installed skill payload version (`.claude-plugin/plugin.json`
   in the skill directory) and record it — transcripts are only comparable
   within a payload version.
2. For each fixture, open a fresh session with the skill active and submit the
   fixture's `## Input` verbatim. Do not paste the fixture's expectations.
3. Capture the full transcript to a file (one file per fixture).
4. Grade each transcript:

   ```bash
   bash scripts/grade-agent-eval-transcript.sh fixtures/agent-eval/<fixture>.md <transcript-file>
   ```

5. Record results in a `docs/audits/` ledger section using this row shape:

   | Fixture | Payload version | Grader verdict | Human verdict | Divergence note |
   |---|---|---|---|---|

6. Where grader and human verdicts diverge, tune the fixture's
   `## Graded properties` (or accept the grader gap with a note) before the
   next eval round. Property changes are payload-affecting only if the
   fixture ships (it does not; fixtures are repo-side).

## Evidence boundaries

- A grader PASS is a properties check, not a holistic judgment.
- One session per fixture is a single sample; do not generalize from it.
- Self-graded runs (the same agent answering and grading) carry author bias;
  label them, and prefer a second judge for the human-verdict column.
- No live run has been performed as of v0.2.9.0; this runbook exists to make
  the first one reproducible.
