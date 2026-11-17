# Report requirement

The local report must reflect the currently selected rendering profile and current jobs data. The heading is the profile heading. After one blank line, render each job in input order as its id, profile separator, label, profile separator, and state. End each line with one newline. Selection uses config/selection.json and config/profiles.json.

A successful build means output/report.txt matches that projection. Reusing a previously computed output is allowed only when it still represents all current effective rendering inputs. Repeating an unchanged build should retain useful reuse. Generated output must be produced through its source owner, build_report.py; do not hand-edit it.

The supplied check compares the output with the exact currently accepted report in expected_report.txt. A previous successful build and previously passing tests do not override a present failing comparison. This is local report behavior only; no external delivery or production claim is requested.
