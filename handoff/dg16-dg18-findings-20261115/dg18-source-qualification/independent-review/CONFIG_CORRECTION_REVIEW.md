# DG18 source-CI configuration correction: independent review

## Result

**No blocking finding in the exact configuration correction.** The correction
addresses the demonstrated GitHub expression-context defect and preserves the
previously reviewed source-only execution and artifact boundaries. The principal
controller owns any guarded engineering publication and receiving of the actual
hosted result. The reviewer performed neither a hosted rerun nor publication.

| Subject | Exact identity |
| --- | --- |
| Reviewer | `/root/dg18_independent_review` |
| Frozen correction commit | `a65c478475c292c74a71ed856a02d0f29c305376` |
| Frozen correction tree | `4675d67a39424ebb7dcfad7671b6c303a1077b37` |
| Local parent | `c9f0ceb93a1cb6503121560de4a92d5d5a35f8c2` |
| Parent/publication tree | `ddf65c6f7e351cf98633598e8dff81f69ccb9bc3` |
| First remote publication | `fbe537794f886b31d85ccd5c665c31ad8070f435` |
| Corrected workflow SHA-256 | `10ac8b5218745ceaa830043b83149126941e5e256056cff56b12c0de40687b2c` |
| Configuration record SHA-256 | `9ca87d8f2b1ab4466150e8660114271c037bc064785a09dda16a18acfcf29c82` |

## First failure and diagnosis

The reviewer independently retrieved [run 43675724954](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43675724954)
and its jobs/artifacts through the connected GitHub API. It is a completed
failure at the remote publication above, with the same creation/update timestamp
and **zero jobs and zero artifacts**. No source CLI case executed in that run.
The readback is retained in `FAILED_RUN_READBACK.json`.

The original workflow uses `runner.temp` in `jobs.source-cli.env`. GitHub's
[context availability table](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability)
does not permit `runner` at that key. The reviewer independently reproduced
the exact baseline refusal with actionlint 1.7.12: exit 1, reporting the forbidden
context at line 27, column 31. The tool binary's SHA-256 is
`c872d6db8c6bf83a8eaa704fc93999f027d55dffbc63b8a6abdccb47df5f4cd4`.

This is a demonstrated source configuration defect consistent with the
immediate zero-job failure. The GitHub server's literal validation annotation
was not available through the attempted reads. The actionlint diagnostic is
local validator evidence and is not presented as a captured server annotation.

The initial independent review's generic YAML and Bash checks did not cover
GitHub expression-context availability. That omission is preserved as a review
gap; the original review records remain unchanged. The original local source
test results and interpreter refusal retain their actual scopes. The hosted
startup failure is not a fixture test failure or a native effect.

## Exact correction and checks

The workflow delta removes one job-level assignment and adds two shell lines
in the existing preflight step. The first exports `DG18_SOURCE_OUTPUT` from
the runner's `RUNNER_TEMP`, run ID and attempt. The second writes that same
value to `GITHUB_ENV` before preflight executes.

This follows GitHub's [environment-file rules](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#setting-an-environment-variable):
the shell export supplies the value in the creating step, while `GITHUB_ENV`
supplies it to subsequent steps. The output remains under the same disposable
runner temporary directory.

The independent check completed **62 of 62 checks**, including:

- Exact correction commit/tree/parent, baseline and corrected workflow hashes,
  and equality of the local parent tree with the actual failed remote run's
  head tree.
- Full YAML structural comparison proving every other workflow setting is
  unchanged: branch/repository guards, permissions, checkout/action pins,
  timeout, selected commands and upload allowlist.
- Before/after actionlint execution using the independently hash-checked binary:
  baseline exit 1 with the expected context diagnostic; correction exit 0 with
  empty stdout and stderr. No diagnostics were ignored.
- All four Bash syntax checks and direct execution of the exact two added
  initialization lines, including a runner-temp path containing a space. Both
  the same-step export and the subsequent-step environment-file record matched.
- Every current manifest member and refreshed workflow/configuration pin;
  preservation of the initial workflow pin and zero-job failure record.
- Agreement of the configuration record with the reviewer's independent run
  readback. The literal-server-annotation field remains null.
- No runtime, fixture, peer, runner-code or prior independent-review mutation;
  `git diff --check` and tracked cleanliness.

The source test bank was not repeated because the correction changes only
configuration evaluation and evidence records. The actual hosted three-case
source result remains pending.

## Authority and next interpretation

This review qualifies the exact correction for the principal controller's
already-authorized guarded source publication. It does not establish a hosted
test pass, original DG18 acceptance, native authority, currentness, merge,
release or issue closure. OR/C02 authentic inputs, W-FULL prerequisites, N1's
missing owner/store/assignment, and complete independent cold receiving retain
their existing gates.

Preserve run 43675724954 as the initial zero-job configuration failure when
receiving any later source run. A later success cannot erase that failure or
turn its zero executed cases into test evidence.
