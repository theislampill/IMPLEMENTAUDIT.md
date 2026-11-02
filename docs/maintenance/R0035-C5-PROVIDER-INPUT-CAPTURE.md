# C5 fixed genuine-provider input capture

`create_c5_provider_input_capture(source_root)` is a separate data-only factory
for the inspected genuine `zopfli 0.2.3.post1` installation. Its fixed captured
source module and selection fixture are additional to the existing C5 route.
Default `PINS`, `_read`, `_Engine.sources`, the qualifier, and the existing C5
system-Python selection remain unchanged. The factory has no run or receipt API.

The fixed provider location is the `provider_root` recorded in
`fixtures/work-graph-c5-inputs/package-venv-python312.json`. This source selects
`/workspace/scratch/112e7cba6e41/work/provider-inputs/venv`; the earlier checkpoint
used `dependencies-g003c/package-venv`. The captured population retains all 28
ordinary files, including the
three real interpreter copies, activation files, `pyvenv.cfg`, installed metadata,
RECORD, native extension, and existing bytecode caches; all ten directories and
the actual `lib64 -> lib` link are observed. Complete directory populations,
ordinary-file modes/owners, single links, bytes, aliases, and ancestors are
checked, with a closing observation. The installed RECORD is verified against
actual captured buffers, including independent fixed hashes for rows that RECORD
does not hash. Wheel payload pins come from the retained genuine publisher wheel;
installation was not repeated or rewritten to make RECORD match the wheel.

The declared child environment selects the real venv `bin/python` first in PATH,
followed by `/usr/bin:/bin`. Normal `site` inputs are observed, including the actual
venv configuration, standard startup code, site namespace, customizer selectors,
passwd/NSS files, and NSCD/loader selectors. The fixture admits no added `.pth` or
customizer. The configuration excludes system site packages; the old system
profile's `coloredlogs.pth` is not relabeled as selected venv startup. Existing
bytecode is captured as bytes. The observer does not construct a `-S` wrapper,
regenerate caches, or import the provider. These observations do not claim that
normal startup or an actual child has already executed.

The native extension's inspected dynamic dependencies add actual
`libstdc++.so.6`, `libgcc_s.so.1`, and `libpthread.so.0` to the already selected
libc/libm/ELF-loader inputs. Their exact resolved bytes, aliases, and ancestors
are fixed. Actual loader-cache bytes and absence of `/etc/ld.so.preload` are
captured rather than inventing an absent host input. Static dependency selection
does not qualify an actual native load.

All actual venv files and native inputs enter the final runtime mapping. The
existing prefix per-file, namespace/depth, mounted-byte, unique-byte, and entry
bounds remain unchanged. The final existing `runtime_budget` check occurs after
all merges. If the complete union exceeds a bound, acquisition refuses and the
raw failure must be retained. Files cannot be omitted or copied-interpreter
mounted bytes discounted to obtain a pass.

Successful data acquisition reports `GENUINE_PROVIDER_INPUTS_CAPTURED`, while
keeping `runtime_complete=false`, canonical acceptance unqualified, and dispatch
count zero. Native execution/custody, actual child identity, Git clone execution,
measured C5 resource geometry, live producer custody, and before-consumer JOIN
remain explicit open gates. The genuine installed provider is not reported as
missing merely because the separate system-Python profile excludes its root.

The three proposed portable controls are positive complete data capture,
currentness refusal after a real test-owned ancestor replacement, and refusals
for added startup code and same-size altered native bytes. The negatives mutate
only disposable copies of the actual installed tree. No original subject,
provider import/compression, namespace launch, or package build is included.
The positive test does not convert a genuine capacity refusal into success.
Source and allocation must be frozen and independently reviewed before control
execution. A later tiny provider import/compression probe requires its own root
admission and supplies no producer, protected-native-subject, or JOIN credit.
