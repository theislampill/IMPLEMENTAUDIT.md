# Three further finite R0035 verifier profiles

This increment adds explicit acquisition contracts for three unchanged original
verifier commands. It uses the existing captured finite factory, compiler,
sealed runtime and isolated executor. It introduces no scheduler, receipt issuer,
source-selection authority or native acceptance claim.

The author evidence is bound to public commit
`e8edae15345b8ae18d4853fa0671c58b3b982847`, tree
`68dabc173c620db05c4fba8495a22c2119f511b1`, plus the finite helper and new cases
in this increment. Later integration requires verification against the actual
receiving source; old receipts retain their original identities.

## Explicit source closures

Indices below are the existing compiler's zero-based original registry indices.
Every scope records all 117 nodes and its 116 omitted nodes. Each executes one
independent original command; none substitutes for a predecessor's effects or
for the complete canonical route.

| Profile | Original index and command | Complete source closure |
|---|---|---|
| `CONTROLLED_TASK_COMMIT_MESSAGE_V1` | 56: `bash tests/commit-message-contract.test.sh` | Exact registry, original wrapper, whole pinned `repo-state.sh`, and all 28 literal commit-message fixtures: 31 files. |
| `CONTROLLED_TASK_AGENTS_BOOTSTRAP_V1` | 59: `bash tests/agents-bootstrap-budget.test.sh` | Exact registry, original wrapper, original checker, `AGENTS.md`, and ordinary `docs/audits/RETENTION.md`: five files. |
| `CONTROLLED_TASK_ANDON_ESCALATION_V1` | 39: `bash tests/andon-escalation-judgment.test.sh` | Exact registry, original wrapper, complete `PROTOCOL.md`, and the five literal escalation fixtures: eight files. |

`contract_for()` accepts only the seven named catalog profiles. The original
four contracts and the audit-spec default remain unchanged. The compiler still
owns graph derivation and exact command identity. The registry SHA-256 remains
`77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`.
Every executable member has an exact SHA-256 pin; unsupported future executable
or registry bytes refuse before dispatch. Data are acquired afresh with physical
ordinary-file custody, ancestor identity and bounded byte counts. Missing,
aliased, special, oversized or changed inputs do not earn semantic-test credit.

The complete `repo-state.sh` source is pinned. The fixed original wrapper invokes
only its `commit-message` branch; unrelated Git and process-substitution branches
are not executed. All 28 named files are required, including expected-invalid
fixtures. Substituting a valid fixture for an expected-invalid one is a real
original-wrapper failure; omitting that file is an acquisition refusal.

The AGENTS checker reads the document and probes whether the retention path is a
file. The profile conservatively acquires the retention file's full ordinary
bytes instead of inventing a placeholder. Textual references in generated
AGENTS fixtures are not additional file reads. The original checker, generated
documents and negative diagnostics execute unchanged.

The escalation script retains its original Bash pipelines, `tr`, `grep -q` and
`pipefail` behavior. Its protocol input exceeds 64 KiB, so this explicit profile
has a 256 KiB per-file and 1 MiB aggregate acquisition bound. This is no permission
to modify executable bytes, replace pipelines or normalize an exit status.

## Runtime and private resource contract

All required tools already exist in the exact captured prefix runtime. The
prefix helper remains
`86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016`.
The source and executable image are read-only. Runtime startup, environment,
stdin, resource limits, process custody, retained output checks and child reaping
continue through the existing owners.

The finite class inherits the existing composed-prefix scratch limit of
33,554,432 bytes (32 MiB). No limit is widened. Reservations use the existing
64 KiB allocation granule plus per-file and per-directory overhead. They include
every possible anonymous Bash here-document spool even where the current shell
uses a pipe or reclaims a spool before the next invocation.

| Profile | Conservative private write population | Reserved bytes |
|---|---|---:|
| Commit-message | 28 possible 3,092-byte here-document spools; no semantic file writes | 3,670,016 |
| AGENTS bootstrap | Three generated documents, three diagnostics bounded at 64 KiB each, seven possible here-document spools, one directory | 1,769,472 |
| Andon escalation | No private file writes | 0 |

The earlier author planning note incorrectly referred to the base qualifier's
8 MiB cap. The actual inherited limit was always 32 MiB; all final acquisition
records show it. The final reservations also fit below 8 MiB. The planning note,
initial source proof and correction remain retained rather than rewritten.

AGENTS temporary outputs are private to the execution namespace and discarded
at its end. These independent profiles do not export their private effects to
canonical successors. Capacity insufficiency refuses before launching or
retaining the runtime image. Existing ownership of no-proc isolation and
contained process lifetime is unchanged.

## Author evidence and original obligations advanced

The preimage rejects all three new profile names as unsupported. The final
helper adds their exact closures and reservations. The focused admission command
is:

```bash
/usr/bin/python3 -B tests/work-graph-finite-next-cases.py
```

It completed 28 admission tests with the three opt-in live classes skipped.
Controls cover exact node/source population, every missing datum, unknown
executable/registry, aliases and special files, byte and private capacity bounds,
raw parent traversal, rejected caller receipts/commands/environments, and
immutable returned catalog data.

In a supported no-proc namespace, the actual opt-in bank was:

```bash
R0035_FINITE_NEXT_LIVE=1 /usr/bin/python3 -B \
  tests/work-graph-finite-next-cases.py -v -f CommitLive AgentsLive EscalationLive
```

It completed nine tests in 41.439 seconds with no timeout and unchanged source
hashes. Each profile has three controls:

1. The original command succeeds; a second request reuses the identical issued
   receipt without another dispatch; changed current data then refuse reuse.
2. An acquired semantic mutation causes the original command's real exit 1 and
   diagnostic. The retained failure cannot be reused.
3. A successful result cannot be reused by a forked foreign producer. Altering
   the retained stdout then refuses with no further dispatch.

Commit-message executed all 28 original fixture decisions. Escalation executed
the contract and five scored fixtures. AGENTS executed its real checker and
original generated negative documents. No output was normalized. A separate
ordinary-host escalation discriminator is retained only as a baseline witness.

The existing four catalog dictionaries are equal to the preimage. Six core
functions (`digest`, `source_paths`, `select_node`, `snapshot_source`,
`finite_runtime`, `bind_session`) remain AST-identical. The old audit-spec,
Andon-class and finite-batch admission suites also exited zero on the new helper;
their opt-in live controls were not replayed or relabeled.

This increment advances finite parts of the remaining original obligations:

| Obligation | Evidence advanced | Remaining boundary |
|---|---|---|
| C1, runtime/startup acquisition | Actual original commands execute from the existing captured runtime with complete new literal source closures. | No claim for other original commands or tools. |
| C2, execution namespace and inputs | Fixed input populations, conservative typed retention probe and exact executable pins; no Git or source enumeration needed by these commands. | Other commands' Git, descriptor and namespace dependencies remain open. |
| C3, mutable resources | Explicit original temporary writes and possible shell spools reserved; insufficient capacity refuses. | No general mutable-effect or global-resource contract. |
| C7, acquire/execute/consume | Actual results, same-receipt reuse, current-data invalidation, failure retention and foreign/altered-result refusal. | No full 117-node or cross-process recovery qualification. |
| C6, predecessor/successor effects | Existing independent-scope boundary preserved. | This increment provides no new successor-effect or accepted-JOIN evidence. |

The three nodes may extend the prior 28-node finite union to 31 only after
independent exact-source review and receiving integration. That would leave 86
original nodes outside the finite union. The original 48 requirements, 20 cases,
eight raw-comparator REDs, Windows/native nonverdicts and accepting-authority gates
remain binding. No whole-issue closure or Pro-exhaustion verdict follows.

## Receiving and publication gates

The public finite factory already accepts named profiles through `contract_for`.
The shared qualifier owner must add only the three explicit CLI names
`commit-message`, `agents-bootstrap` and `andon-escalation` to `_FINITE_MODES`.
The existing verifier wrapper must register this case file once, with its exact
expected-child list updated. The original `verify-package.sh` registry and 117
nodes remain unchanged. Do not create another factory or test wrapper.

This helper, case file and maintenance note are repository-only paths. The
canonical payload selector does not ship them; no runtime member is removed or
excluded by this increment. Commit/tree inventory bytes still change on
publication, so the receiving owner must measure the actual final artifacts and
preserve the 458,752-byte cap and 2,000-byte reserve. The unresolved four-source
combined package is a separate gate.

The shared qualifier, compiler or custody-loader proposals may change before
integration. Merge them serially, preserve exact preimages, and review/test the
resulting source rather than carrying these receipts forward under another hash.
Independent review, actual receiving package/install checks, guarded publication
and hosted CI remain receiving-owner gates.
