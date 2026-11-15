# Actual W-FULL preparation failure received

**Received an authentic failed preparation, not an operation ready for grant. Authority: NONE.**

Run `43715783204`, attempt 1, job `132816896036`, was the ordinary push at source publication `2728929b536c2404ebb5a6e8778503f6aac40f34`. Actual GitHub ref and commit readbacks bind tree `39f098b04aea81f872d5834b235abf9b9d08f2ce`, sole parent `ef7bfa0590876f6a92ebe3dcdc833829f0d43c09`. The nine-file publication matches the independently reviewed source and retained review bodies.

Actual provider logs identify Windows Server 2022 / image `20261112.366.7`. Workflow step 5 failed; step 6 successfully retained the artifact. Commands 001–008 completed. Command 009, exact controller activation, returned 1 with:

> claim-run.sh: initialization validation refused: read-canonical-pair: directory spelling aliases a different canonical long name
>
> validate-run-root: ERROR: canonical pair selection refused; root compatibility fallback is forbidden

The actual claim and pending initialization token are retained. The archived authority namespace contains only the pending initialization ref: no current-controller binding, pointer, receipt or migration marker was published. First resume, first rotation, explicit manual invalidation and maintained prepare were not reached. **OPERATION.json does not exist; there is no operation hash to put into a native grant.**

The artifact was acquired once: ID `14162372472`, `612663` bytes, SHA-256 `4bb9cce7c9c239c49b02b973d53d884a810d9709c0d77b1309680a9c976fac6e`. All 29 members passed CRC and SHA checks. `SUBJECT.tar` is preserved at 2,406,400 bytes / SHA-256 `7c6690005e55e0ec14f3d6ed2efd24aeb9a0c42e7409eb7841ac6bb19189e1f2`. Its complete member manifest, actual copied source equality, Git object hashes and authority-ref facts are in the companion receipt. No subject code was executed locally.

## Narrow diagnosis

The actual retained TEMP/TMP values are `C:\Users\RUNNER~1\AppData\Local\Temp`. The maintained activation owner creates a default temporary validation copy, passes that exact path into the unchanged validator, and its first canonical read compares each supplied directory spelling with the actual Windows long handle name. That route explains the observed alias refusal. The stderr does not name the individual rejected absolute component, so this is explicitly a source-supported causal diagnosis rather than an invented runtime path trace.

Normalizing only existing TEMP/TMP through the existing physical-path checker before environment construction is the bounded integration remedy. It must preserve the existing symlink/reparse and canonical-name checks, retain the actual corrected environment, and receive the final exact source and a real corrected preparation separately. Nothing was retried or changed by this reviewer. The failed subject, raw bodies, original publication and prior source review remain preserved.

The receipt grants no native execute, measurement result or original acceptance. A successful actual preparation, fresh operation-specific owner grant, applicable concurrent owner originals and actual measured-result receiving remain necessary.
