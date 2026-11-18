# Independent live-control transport diagnosis

## Identity and scope

- Reviewer: `/root/g2_delivery_checks`.
- Date: 2026-11-18 UTC.
- Host/self-reported model: GPT-6 Astra Pro; exact provider deployment ID is not exposed.
- Authority: NONE. Read-only source diagnosis and bounded local transport diagnostics only.
- Actual episode: repository `theislampill/IMPLEMENTAUDIT.md`, run `44239735578`, attempt `1`, workflow `9a349423b6ca3dda18115a07ed41b63970bc8b77`.
- Parent-reported published control: `0fc8b8a0343925e72b24f4f98daad8ba988bd045`, verified by Root at 07:41:52 UTC. This report does not independently claim hosted consumption of that commit.
- No running code, branch, requirement, source, proof, review, Root choice, original deadline or M2 oracle was changed. No accepting operation was relaunched or replayed.

**Conclusion:** the pinned source has a concrete integration defect: the live consumer attempts HTTPS Git reads through a utility that denies all Git transport by default, without an operation-specific HTTPS permission. It then treats the resulting fatal exit 128 as an absent branch. This source chain, Root's exact-environment local RED, and the rehearsal environment difference explain why a published control can remain unseen. The exact hosted stderr has not been observed in this task; the hosted causal attribution is an inference from the pinned executable path, not a fabricated hosted log result.

## Evidence identities

| Evidence | Identity |
|---|---|
| Selected `host_utility.py` | SHA-256 `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5`; Git blob `686e55cc37e0483495353ff6f4065dd8fa9bd672`; 65,235 bytes |
| Selected `live_control.py` | SHA-256 `05918b2d5c2f791a92c52fd72cf795a870f24ddedc1c6867fbbf358218cb400a`; Git blob `1e63965231b8ceffaa9fb1526bf7224305ca3918` |
| Selected `run.py` | SHA-256 `1b03430baef6ba14221f6f22050f1d681c3491ce887fccdf49d434dd45a5ac68` |
| Root's `EXACT_SAFE_ENVIRONMENT_RED.json` | SHA-256 `99d3beeedccab44979c9518ef90f71d4845b7ac7cc456a0d786d1e9dbdbeb94d` |
| Prior `rehearse_control.py` at integration checkpoint `afda760d6de5cac08a27ad86da4c2be981749354` | SHA-256 `822b81e09d8866341762873bdcfae21c925262848b74190bcde18e4b546be734`; Git blob `c14ef105f56333eb1e78f9b1920e9e61b29852a6`; 5,760 bytes |
| `INDEPENDENT_HTTPS_OVERRIDE_DIAGNOSTIC.json` | SHA-256 `6b9e13147bbb12978f46b9c2422edbf2fe949193177e0b76f7cd7b5cf373d19c` |
| `INDEPENDENT_HTTPS_OVERRIDE_FOLLOWUP.json` | SHA-256 `b3965de607740a526e4673ba84d5bd2a0353902b1e022fef0b5dae01e6c0ccf5` |

The selected utility and consumer identities are bound to the immutable workflow tree. The utility's local Git blob hash was independently recomputed and matched. The prior rehearsal source was fetched at the immutable integration checkpoint and saved as `rehearse_control.afda760.py`.

## Causal chain in the exact selected source

1. `run.py` pins and loads the exact utility through `UTILITY_SHA`, then passes that utility to `live_control.hold` during the hold step.
2. `host_utility.py:588–594`, `safe_environment()`, supplies a closed child environment. It sets `GIT_CONFIG_COUNT=3`, `GIT_CONFIG_KEY_2=protocol.allow`, and `GIT_CONFIG_VALUE_2=never`. Global/system config is disabled, prompting is disabled, and the other capture restrictions remain fixed.
3. `host_utility.py:693–697`, `capture()`, always calls `subprocess.Popen(..., env=safe_environment(), ...)`. Parent ambient Git permissions are not inherited through this boundary.
4. `live_control.py:98–107` sends plain `[git_path, *arguments]` to that capture. Its fixed HTTPS `ls-remote` has no protocol-specific override. The later fixed-URL fetch at line 121 has the same defect.
5. Root's exact-environment local command returned 128 with the fixed Git transport-denied message. This occurs before the remote branch can be read.
6. `live_control.py:103` treats both 2 and 128 as missing when `missing=True`. `head()` enables that behavior. Consequently the fatal transport refusal becomes `None`, the loop never reaches the control commit, and it continues the original approximately 15-second polling until the unchanged deadline.
7. A changed publisher branch cannot repair this transport boundary: the consumer cannot read that branch. A normal successful native Git call outside this exact capture environment does not contradict the refusal.

Git's official documentation confirms that `protocol.allow` supplies the default for protocols without a specific policy; `protocol.<name>.allow` selects a protocol-specific policy. Explicit `git -c` options override runtime environment configuration. `ls-remote --exit-code` uses exit 2 for no matching refs; generic fatal 128 is not that condition.

References: [Git configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-protocolallow), [runtime configuration precedence](https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT), [ls-remote exit status](https://git-scm.com/docs/git-ls-remote#Documentation/git-ls-remote.txt---exit-code).

## Why the rehearsal did not detect it

The earlier rehearsal uses `ReadOnlyCapture` at `rehearse_control.py:57–67`. Its `subprocess.run` at line 64 has no `env=` argument, so it inherits the rehearsal process's ambient environment. At lines 101–102 it supplies this replacement capture adapter to the original consumer.

The original consumer's source was exercised, but its production capture environment and original host utility integration were not. The prior independent delivery assessment already limited its claim to synthetic transport/reservation mechanics and explicitly withheld original host utility descendant-reaping, timeout-cleanup and adverse-network qualification. Its observed successful synthetic transport remains valid at that scope; it is not evidence that HTTPS was available through production `safe_environment()`.

## Independent bounded discriminator and its limit

I extracted the literal `safe_environment()` dictionary with Python AST, without importing/executing the utility module. With only the prospective Git argument `-c protocol.https.allow=always` added:

- Effective `protocol.allow` remained `never`.
- Effective `protocol.https.allow` became `always`.
- The local `ls-remote` error changed from Root's transport-denied RED to **DNS_HOST_UNRESOLVED** for the fixed public GitHub host, exit 128.
- No timeout or control observation occurred.

Thus the narrow override removes the demonstrated protocol-policy obstruction while retaining default denial. **It has not been demonstrated here to complete remote transport, fetch, control consumption, or original host-capture custody.** The scratch DNS observation is not evidence of hosted-runner DNS failure. The local diagnostic used a bounded standalone subprocess, not original `utility.capture`. No ambient proxy/credential environment was imported or proposed as a workaround.

## Smallest legitimate prospective repair

Keep `host_utility.safe_environment()` and `capture()` unchanged. Within the selected live-control owner, add `-c protocol.https.allow=always` only to the two fixed-URL remote operations:

- `head()`'s `ls-remote`, covering both initial and final head reads;
- the exact-commit `fetch` into the private bare cache.

Do not broaden `protocol.allow` to `always`, inherit the full parent environment, enable SSH/file/ext transports, alter the fixed remote, or bypass `utility.capture`.

Also distinguish missing-ref status from failure: only `ls-remote --exit-code` status 2 should mean an absent selected branch. Its 128 transport/config/auth/network failures should reach a bounded refusal rather than consume the entire hold as apparent absence. Preserve any separately intended missing-local-subtree handling explicitly at its own call site; do not retain a common all-128-is-missing rule for remote reads.

This preserves the original pidfd/descendant cleanup, stream bounds, per-command timeout, monotonic/UTC deadlines, sole-parent/tree/population checks, stable-head readback, and exclusive durable reservation. No review schema, correspondence relation, proof or original M2 predicate needs weakening.

A prospective immutable candidate must update the changed consumer digest and its transitive adapter/workflow/decision seals through the existing review/adoption rules. That cannot retroactively alter this running pinned episode or make its already issued request reusable after expiry.

The meaningful qualification gap is the exact production boundary: test the repaired remote reads through the original capture/environment on a host with the intended network, plus absent-ref status 2 versus fatal 128, retained default denial, and unchanged deadline/cleanup/reservation behavior. Repeating only the ambient-environment rehearsal would leave the causal gap open.

## Current receiving boundary

This diagnosis is not terminal M2 receiving and establishes no live consumption. Preserve the actual provider terminal result and any available bounded original capture evidence. Do not relabel local diagnostics as hosted output, extend the live window, mutate the running source/control tuple, or issue retrospective consumption. The original M2 oracle report remains unchanged.
