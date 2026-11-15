# Independent review: bounded DG17 installed consumer

**Disposition: PASS for the exact source/static review scope below. Hosted execution and independent receipt of its actual outputs remain pending.** This report is evidence only. It grants no launch, acceptance, publication, currentness, or closure authority.

Reviewer: delegated `/root/g2_receiving`, separate from the candidate author. Read the supplied commission, actual AGENTS.md, candidate adapter/workflow, and the relevant existing product owners. Owner steering supplied by Root controls the present scope: zero Claude/Codex model operations and no owner-PC task. No product source was edited, committed or published by this review. No task was initialized or accepting installed consumer run locally.

## Exact reviewed population

Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/dg17`. Baseline product commit `a297957be11feb494c0ec467235794a1e0c54751`, tree `b08dc4ecf4028beeedb579a312eccae23cb5d863`. Only the following two candidate paths differ from the baseline; the workflow pins the adapter digest exactly.

| Candidate | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/dg17-offline-lifecycle.yml` | 7803 | `5001ad9035af7cca66a6ebe7c23c433b71383fea0fee3b1613bd62a61b1e7ae1` |
| `handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools/installed_nonterminal.py` | 19264 | `7a9cd9f9d4b0e31d57c4475374ab706ef860d2d8a1a9db40389f3b6769515eba` |

The earlier `6565546e…` / `20044c52…` packet is superseded by this freeze. No verdict is attached to an unspecified later edit.

## Findings and supported composition

| ID | Severity and disposition | Owner/source and reproduction | Implication and correction/verification |
| --- | --- | --- | --- |
| DG17-IR-01 | Medium; resolved before this freeze | Adapter `fact()` and `host_context()`. The earlier metadata call inherited the evidence-member `st_nlink == 1` rule for resolved system binaries. A legitimate package-manager hardlink could therefore refuse before installed Python admission. | The frozen adapter calls `fact(actual, single_link=False)` only for root-owned, non-group/world-writable physical tool ancestry. Evidence and package populations retain the default single-link rule. Reviewed the precise correction and the author's retained RED/GREEN control records; no duplicate test or hosted run was spent. |
| DG17-IR-02 | Informational; supported | Workflow and adapter source identity, `prepare()` and `installed_parity()`; existing `package-contract.py:625–722` and installer. Read the exact CLI forms and owner code. | Packet is checked out at the event SHA; product is independently checked out at the full fixed a297 commit. Clean HEAD/tree are checked before and after. Existing package verification binds archive identity and complete member bytes to that checkout. Existing installer receives the exact canonical archive/checksum in a fresh sentinel-bearing root. Adapter compares the complete installed file population, byte lengths, hashes and modes with the archive, before consumption and again afterwards. No source205 archive is substituted. |
| DG17-IR-03 | Informational; supported | Installed `claim-run.sh:460–510`, `claim-run-rotation.py:4408–4778`, existing `author_checkpoint.py`, and adapter initialization. Reconcile supplied arguments with each parser and selected control flow. | Claim allocates pending custody; actual fresh documents are authored before inspection and exact-token activation. `READY_TO_DISPATCH`, phase 1, open audit object, concrete next action and pending receiving decision are permitted. The paired initialization validator hash/length matches the exact existing validator. The adapter requests normal currentness after activation; activation is never treated as the receipt itself. |
| DG17-IR-04 | Informational; supported with explicit ceiling | Separate workflow read actions, adapter `consume()`, installed `claim-run.sh:295–337`, and `read-canonical-pair.py:425–457`. | STATE is read first and ROADMAP in a distinct subsequent workflow action. Document population is checked across the reads. The authored actual G0001/new-session row binds the disposable subject's real commit/tree. The existing fresh legacy receipt path permits absent prior invalidation. Resume, exact receipt verification and required currentness use installed public owners. This fresh task has no canonical migration authority, so the existing authenticated legacy profile applies; no typed canonical migration or protected native admission is demonstrated or claimed. |
| DG17-IR-05 | Informational; supported with explicit ceiling | Existing `validate-run-root.sh:2023–2245` and adapter `consume()`. | Both installed and source validators consume the same real selected task and must exit zero with identical stdout containing the existing nonterminal result. The owner explicitly labels that predicate `source-only; host enforcement unavailable`. The adapter additionally requires identical currentness before/after, unchanged Git refs, unchanged governed records, unchanged installed payload and clean exact product source. The result may describe actual installed nonterminal consumption; it cannot describe genuine native Stop or original DG17 acceptance. |
| DG17-IR-06 | Informational; supported | Workflow branch gates, adapter environment and operation list, always-run artifact step. | Only the new ordinary installed job is eligible on `engineering/pro-executor-dg17-installed-20261115`; both old simulated/source suites are gated to their original source branch. There is one current-source build/install/task sequence, no canonical suite, model command, native event synthesis or grant. Exact command captures and metadata, actual receipt blob, task runtime records (including hidden members), archive bodies and checksums are retained. Failures remain failures; the adapter writes step failure metadata after the evidence directory exists. |

No open blocking source defect was identified in this frozen population. Runtime host eligibility, dependency acquisition, exact compressed package size and actual owner outcomes still require the proposed ordinary hosted execution; static review does not predict them as passed. Existing budget revision 5 is unchanged: canonical cap 589824/reserve 1240; standalone cap 589824/reserve 2000. A budget failure remains a failure.

## Independent verification performed

Performed one bounded read-only source check, without executing an owner or constructing a task: Python AST parse; exact workflow adapter pin; branch gates and separate step order; byte comparison of ten invoked product source files against their a297 Git blobs; exact initialization-validator paired hash/length; and pure string evaluation of the candidate's required STATE-field patch against the unchanged template. All passed. `git diff --check` also passed. Candidate hashes were observed directly.

The candidate author's YAML/Bash syntax/CLI checks and local scope-refusal record were read as author evidence; they are not misrepresented as independently rerun here. The existing broad Linux/Windows qualification suites were not repeated.

| Existing source | Bytes | SHA-256 |
| --- | ---: | --- |
| `fixtures/controller-initialization/author_checkpoint.py` | 9582 | `fa875136c9b856027232387afc32bb788d7f728bb082b029b046cea74b02fecb` |
| `skills/implementaudit/scripts/claim-run.sh` | 32290 | `0815c06589f657a2ae467f7ebc1d106e6f0cc425f4b99ee4edce6b38ce5db353` |
| `skills/implementaudit/scripts/claim-run-rotation.py` | 291624 | `866e9f669625fe3df29a3b3f4ff58f32d77a8a4b905ff8d6bffc9ef34561e42d` |
| `skills/implementaudit/scripts/validate-run-root.sh` | 123126 | `7787569b4bceb541c33ee3287f0a8297882caff5478687e84fc534077e4c28ad` |
| `skills/implementaudit/scripts/read-canonical-pair.py` | 27208 | `c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8` |
| `scripts/build-release-asset.sh` | 29407 | `ff22936cb014647e3ea6884e88de65c6cd97a1d9930171fdae205be300adf708` |
| `scripts/install-plugin-from-release.sh` | 3158 | `fa06b9059be0649865af75b7e11ba4a81bb0e3d284b2a1f039092e8f9d9b111a` |
| `scripts/package-contract.py` | 46034 | `506d52a9e12261c295a1bf0fe16e4cf4c382ec06335feeb8806f404396568c1f` |
| `package/implementaudit-package.json` | 5617 | `c4844781b4063e02f8fbe33dea67937d3efb3c913f726583c10a0d41387f9c2e` |
| `requirements-release.txt` | 20 | `cfb500c2279c57e8af17a1a4db8a5f43878160a06f7e6de655d39bfa2e7f0117` |

## Receiving boundary

Receive an eventual hosted result only at its observed scope after provider/run/source/artifact readback. The candidate truthfully keeps native Stop, native host discovery and original DG17 acceptance false; model turns zero; independent receiving pending; the audit object open; and fourteen historical custody differences UNKNOWN. This source review does not revise any of those dispositions and is not an original-row award.
