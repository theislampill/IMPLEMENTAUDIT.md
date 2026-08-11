# Sidecars

Use Graphify only for unfamiliar, majority-code, terrain-shaped work lacking a
one-search answer; otherwise search/read/Git. Graphify is orientation only.
Live files remain proof. Graphify absence does not block consumer runs.
IMPLEMENTAUDIT self-maintenance may use Graphify; no sidecar output enters the release package.
First run: detect only optional tools with a shipped detection route; TokenSave
remains explicit/on-demand. Document install or usage commands; install or
configure tools only after explicit authorization; index/export/write
sidecar outputs only after separate explicit authorization. No silent install.
No silent indexing. Storage is representation-specific: Graphify catalogues stay
outside the repo. TokenSave's separately authorised repo-local database is the
representation-specific exception; keep it untracked, non-packaged and
retention/cleanup-disclosed. ActiveGraph custody stays in the governed run root
or an authorised temporary path.

A strict outside-repo `schema: 1` catalogue binds graph/digest, parent, canonical
scan root, rules/files/config, build and `llm: false`. `--graph-scope <catalog>
<repo> <path> [path...]` selects smallest fresh; `--graph-parent <catalog> <repo>
<scope> <reason>` revalidates then broadens once. `relation-omission` routes an
extractor/relation-model omission to live census. `stale-sidecar`, symlinks and
info/global excludes fail closed. Legacy `built_at_commit` uses
`--graph-freshness <graph.json> <repo-root>` against `git rev-parse HEAD`.

After authorised extraction, Graphify 0.8.37 `manifest.json` is an object of
scan-root-relative keys and exact `mtime,ast_hash,semantic_hash`/32-hex rows.
Prefix keys by canonical repo-relative `root` (`.` = repo); sorted `files` maps
live SHA-256, with `file_count` its length. Root-prefix each relative
`source_file`; its unique set equals `files`. Sorted unique `include`/`exclude`
define scope; sorted `config` maps `.graphifyignore`, `.gitignore`,
`.graphifyinclude` from repo through root to SHA-256/`null`. Active nested
ignore/any include is `unsupported-config`.

Exact keys: top `schema,scopes`; row `name,parent,root,include,exclude,file_count,
files,config,graph,graph_sha256,build`; build `commit,tool,version,mode,llm,
rules_sha256,scope_sha256`; unknown/duplicate keys fail. Canonical UTF-8 JSON is
`json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)`.
`rules_sha256` hashes sorted rules; `scope_sha256` the row minus graph fields/
itself. Inject at `graph.implementaudit_scope_sha256`; serialise; set
`graph_sha256`.

## Privacy and spend

Graphify 0.8.37 lacks `--code-only`; `--no-cluster` lost terrain. Reject
`llm: true`. Semantics need positive/no-LLM cells and owner-named backend;
auto-detection authorises nothing. Content may leave; a filename heuristic
filters it, and zero may mean unmeasurable spend.
Ollama is explicitly unauthorized: "owner said Codex, not Ollama".

Dogfood-only (Windows/graphifyy 0.8.37, 2026-08-09): release beat root once;
both missed a variable-bound call. Luna/partitions remain unproved; an
unfamiliar third-party repo gates broadening. The missed-use-detection goal is retired.

TokenSave is optional code navigation, not another terrain or custody authority.
Use it only when a supported code-relation question makes a repeated or
transitive source walk worthwhile. A `current` classification requires an exact
checkout/database binding and a successful sync/reconnect witness for that same
binding. Missing, failed, stale, wrong-worktree, branch-unknown or unverifiable
binding routes to live Gemba. Classify the result as `TokenSave-derived`,
partial, stale, unsupported or unresolved, then confirm consequential findings
in live source. Database
freshness proves only the represented population: unsupported languages,
extraction failures, dynamic dispatch, generated code and external dependencies
remain outside it. Same-name/cross-language conflicts fall back to Gemba.

Documentation, policy, public projection, non-code artefacts, an exact supplied
file and tiny reversible work are `NO TOKENSAVE` cheap paths. Presence authorises
no install, indexing, config or ignore edit. Repo-local state may retain complete
function bodies and rendered-source cache; keep it untracked, disclose documented
metadata network calls, and clean it deliberately. Editing, test-running, session
and memory tools stay outside supported use. Impact is not edit authority;
affected tests are not acceptance; TokenSave plus Graphify is not independent
corroboration. Absence never blocks ordinary Gemba.

ActiveGraph: authorised `fork` / `diff` or non-authoritative mirror; run root
stays authoritative. Replay proves only supported recorded graph state; events,
forks, diffs, trials, promotion, snapshots and idle state establish only their
recorded state, lineage, structure, declared process boundary, graph update,
local integrity or quiescence. External effect, observation completeness,
semantic correctness, independence, owner authority, host security, engineering
closure and distributed correctness require independent evidence at that owner.
With no durable causal/counterfactual need, use no ActiveGraph.
Never ship sidecar/run-root output, `custody.db`, graphs/caches/JSONL. Prove
manifest equality, checksums, install-copy smoke.
