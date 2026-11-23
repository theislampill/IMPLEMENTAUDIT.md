# DG16 M5 canonical reserve and scoped v5 approval

**Keep the original M5 v4 shortfall open at the exact current source.** The existing v5 approval applies to the reviewed DG17 interlock correction. A source-native deduplication trial did not recover headroom. The exact current installed consumer evidence remains received at its declared overlapping scope.

| Exact canonical archive | Source | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Historical original M5 | `205aeab7c93299b0666b261485ab5658d8e183de` / `9ffbaf95080092bf4a45b8772a97ed16068544a7` | 584,971 | `a43f018d4d3cc6d6257eeacfd8b5b834588410564ac33b0c8022d01a0ca71e58` |
| Current composite | `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` / `9c3913ceaa95f3f36b0377fe2dba4a302afcba89` | 588,564 | `12502ae8c75dfc5127aec7b6c038ee0fe12e191c9976cef3b5545503d64e0aa8` |

Both exact ZIP bodies were read back and compared. Each has 75 members in the same order with the same modes, host metadata, timestamps and DEFLATE method. The immutable build records identify the same canonical compressor. Their compressed difference is 3,593 bytes, entirely accounted for by changed members. The largest changes are `validate-run-root.sh` (+2,255 bytes), `host-stop-interlock.py` (+1,046) and `PROTOCOL.md` (+266). The comparison made no changes to these files or the archives. [Historical exact archive](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/c073689e315b4db7c26e5a95c9024a34b1e560b7/handoff/dg16-m5-source-20261115/validation/new-package-fixture-build/artifacts/IMPLEMENTAUDIT.plugin.zip), [current exact build receipt](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/c41ad7df2d723e371e4684c4070a01902a110971/handoff/astra-dg16-dg18/ROOT_RECEIVING_02.json).

The original v4 cap is 589,824 bytes with a 2,000-byte reserve, so its usable ceiling is 587,824 bytes. The historical original archive clears that by 2,853 bytes. The current archive has 1,260 bytes of physical reserve and misses the original floor by **740 bytes**. It clears the v5 ceiling of 588,584 bytes by 20 bytes. The original M5 receiver checks revision 4 and its exact approval and reserve fields as well as archive size. Shrinking bytes would address one predicate. It would still leave the v5 revision and approval identity to be received under the original contract. [Original receiver source](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/c073689e315b4db7c26e5a95c9024a34b1e560b7/qualification/dg16-installed-runtime05/installed_runtime.py), [original M5 exact-source decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuation-recovery/m5/ROOT_ORIGINAL_RECEIVING.md).

The primary v5 owner decision narrows the reserve exception to the independently reviewed DG17 correction and its necessary package-contract integration, and excludes acceptance certification. The current Root receiving decision explicitly preserves the distinct v4 and v5 predicates while receiving the four current installed consumer chains at their applicable scope. DG18 C11's received v5 applicability on this composite stays at that episode's scope. Neither changes the required original M5 predicate. [Exact owner decision](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/package/budgets/pr255-v5-owner-approval.md), [current Root receiving](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/c41ad7df2d723e371e4684c4070a01902a110971/handoff/astra-dg16-dg18/ROOT_RECEIVING_02.json), [C11 independent receiving](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/c41ad7df2d723e371e4684c4070a01902a110971/handoff/pro-executor-results-20261115/continuing-execution-20261120-18/DG18_C11_INDEPENDENT_REVIEW.md).

## Source-native trial rejected

The planning validator independently reads the phase document and scans repeated list-item grammar for current-state excerpts, evidence and maintenance notes. The trial uses one snapshot and a common parser for those three ordinary content checks. It preserves each section's placeholder phrase, the maintenance-only horizontal-rule boundary and existing normal diagnostics. The exact old Python blocks and the trial's Python block agreed on failure counts and stderr in all 125 combinations of missing, valid, placeholder, horizontal-rule and blank entries across the three sections. The inputs were constructed text fixtures. No Windows custody, containment, resource or safety predicate entered this trial.

The pinned package contract's canonical Zopfli 0.2.3.post1 produced the current member's actual DEFLATE bytes bit-for-bit. The trial member shrank from 45,816 to 44,208 raw bytes. Its compressed size **grew from 12,014 to 12,195 bytes**, a 181-byte increase. Holding other members fixed for attribution gives 588,745 bytes before any updated inventory. These are measured member bytes, without a new archive build or source selection. The exact trial source SHA-256 is `9a2cfcaa2fe819a7d115e310c6bcbcbafcd9d8861c4a87a5cad1e09d18353ad3`. Reject this trial for M5 headroom. No defensible reserve-recovering change was identified in this bounded evaluation. Shipped source, package definitions, installed evidence and the original acceptance decision were left untouched. [Current validator](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/skills/implementaudit/scripts/validate-phase.sh#L934-L1034), [canonical compressor](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/scripts/package-contract.py#L399-L438).

The rejected measurement case replaces the exact source region from `  # Check: current-state excerpts section` through the line before the enclosing `fi` with the following. It remains an inert trial specification.

```bash
  # Check the three required content sections against one phase snapshot.
  if section_errors=$("${py_cmd[@]}" - "$phase_file" <<'PY'
import re, sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
base_placeholder = r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|"
sections = (
    ("Current state excerpts", r"current state", False, "", ""),
    ("Evidence required", r"evidence [0-9]", False, " `- <evidence>`", " (- <evidence>)"),
    ("Maintenance notes", r"maintenance note", True, "", ""),
)

def contains_item(heading, placeholder, stop_at_rule):
    header = re.compile(r"^##\s+" + heading, re.IGNORECASE)
    boundary = re.compile(r"^---\s*$|^##\s+" if stop_at_rule else r"^##\s+")
    in_section = False
    for line in lines:
        text = line.strip()
        if header.match(text):
            in_section = True
            continue
        if in_section and boundary.match(text):
            break
        if in_section and text.startswith("-"):
            item = text[1:].strip()
            if item and not placeholder.search(item):
                return True
    return False

errors = 0
for heading, suffix, stop_at_rule, detail, trailer in sections:
    placeholder = re.compile(base_placeholder + suffix, re.IGNORECASE)
    if not contains_item(heading, placeholder, stop_at_rule):
        errors += 1
        sys.stderr.write(f"validate-phase: ## {heading} needs at least one non-placeholder{detail} list item\n")
        sys.stderr.write(f"validate-phase: ERROR: ## {heading} needs at least one non-placeholder list item{trailer}\n")
print(errors)
PY
  ); then
    errors=$((errors + section_errors))
  else
    err "required phase content validator refused"
  fi
```


## Higher compression effort rejected

A source-neutral in-memory control read the exact 588,564-byte composite ZIP and verified its archive digest, CRCs and 75-member population. With the pinned Zopfli 0.2.3.post1 implementation and all other current options fixed, increasing iterations from 15 to 30 reduced the sum of compressed member-body lengths by **109 bytes**. All 75 alternate raw DEFLATE streams round-tripped to their original member bytes. Holding ZIP overhead and inventory bytes fixed gives 588,455 bytes, **631 bytes above the original ceiling**. This bounds that alternative. No archive was written, compressor or budget contract was changed, or installer or host operation was run.


## Duplicate implementation screen

A declaration-level AST census of the 12 Python members in the exact 75-member archive found one identical top-level declaration at or above 300 source characters: `_windows_custody` in the pair reader and state-rotation owner. The candidate concerns Windows custody. A controlled compression comparison omitted one copy at a time in memory without running either source body. Omitting 1,398 raw bytes saved 362 compressed bytes in the pair reader or 280 in the rotation owner. Each calculation used the pinned compressor and reproduced that member's original compressed length in the unchanged arm.

Neither omission reaches the 740-byte shortfall, even before supplying a replacement call path. The calculation proves only the compressed effect of those exact omissions. There is no semantic or packaged candidate to review. Preserve both custody implementations and the original reserve gate.
