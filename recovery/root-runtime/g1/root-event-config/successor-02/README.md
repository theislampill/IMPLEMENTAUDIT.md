Usable successor CLI: `g1_event_config.py`, SHA256
2c35134f65ea5354ca50cb8e7767196e3b5ce45d13d6833c2bb8140286873eaa.
The predecessor remains untouched. No actual grant, provider call, host/control
publication or native operation was performed while preparing this successor.

Selection now matches ROOT_READBACK_FRAME_HANDOFF35359307…d60a:

- Control: receiver-02/root-control-v5/control_process_v5.py,
  SHA1f78c843…cdff; callbackv6 SHA7760fd14…0734.
- Its same-directory peers are control_readback.py SHA7e7d26fa…a649 and
  file_readback.py SHAab938a99…4cb1. Root's exact installed directory is
  `/home/agent/dg16-g1-current04-operators/public-receiver-02/root-control-v5/`.
- Control configuration and admission schemas are v2. Admission carries the
  exact readback_contract: metadata github_fetch, file github_fetch_file,
  immutable published commit, both peer hashes, maximum frame45 seconds.
- Seven-slot artifact roles remain role_process_v4 cd9e9f34…06a0 and its
  unchanged v1 role admission/profile. Binary's separate c381d6… control_v3
  Journal/guard dependency is preserved; it is not replaced by control_v5.

Root can invoke the verified CLI from its installed copy or the exact reviewed
source mapped into WSL. ROOT below is the existing public-receiver-02 path.
The ready no-duplicate-fetch path is:

    /usr/bin/python3 -I -B CLI inspect-role-from-status ACTUAL_ROLE_INPUT.json ROOT/event-configurations/UNUSED_NAME
    /usr/bin/python3 -I -B CLI issue-role-from-status ACTUAL_ROLE_INPUT.json ROOT/event-configurations/UNUSED_NAME

The second command is an actual Root issuance, only for Root to invoke under
its existing authority. The first issues/writes nothing. Exact input fields:

    schema: dg16.g1-root-role-status-issuance-input.v1
    phase: tools | recipient | g3_initial | g3_final | terminal | failure
    context: {repository, branch, workflow_commit, workflow_path, run_id, run_attempt, job_name}
    window_opened_unix_ms: actual original Root role-window start
    deadline_unix_ms: actual unextended expiry
    publication_receiving: {path, sha256}
    status_readback: {path, sha256}
    shell_title: actual received WindowsRoleIO shell title
    initial_session: null, except actual initial Session for g3_final
    actual_root_decision: null, except {path,sha256} of original first Root body for g3_final

`publication_receiving` points to the single Root-authenticated
ROOT_PUBLICATION_RECEIVING.json with exactly:

    {ref: actual /git/ref/heads/branch body,
     commit: actual /git/commits/head body,
     run: actual /actions/runs/run_id body}

`status_readback` points to exactly `{job,artifact,observed_unix_ms}`: the actual
current selected job object, exact selected artifact-listing row and actual
observation cutoff. These are original provider bodies, not manufactured tool
wrappers. Root independently authenticates/retains their actual calls/history.
No additional metadata GET is requested by this path.

The publication receipt binds ref, sole-parent commit/tree and actual run/head/
repository/branch/attempt. Its historical run.status is not current and does not
force a repeat GET. Fresh selected job status plus selected artifact identity,
phase name, digest/size, run/repository relation and chronology govern current
phase eligibility. The current cutoff must lie in the original window. The
role's own seven-slot metadata/download receiving remains mandatory and intact;
this preconfiguration does not substitute for it or assert unseen census data.

Context must be the approved f9ba187e8f5520956f0f16cf13c0a706e8360b96 job on
pro/dg16-g1-original-g3-04-20261109, workflow
.github/workflows/dg16-r5-g1-hosted-episode.yml, run_attempt1, job_name qualify,
repository theislampill/IMPLEMENTAUDIT.md; run_id is the actual provider run ID
as a decimal string. Commit tree8390375505282e602759c7976b6bca82a44d5737 and
sole parent7e2b00b3a2a16fc6033a5eabe4fc795f6249366f are checked.

The earlier inspect-role/issue-role four-result input remains optional for
already captured authentic results; it is not a prerequisite for the status
path and must not cause duplicate acquisition.

After actual tools receiving, the unchanged tools-decision commands construct
only the real requirements' fixed body plus Root's actual issuance/expiry:

    /usr/bin/python3 -I -B CLI inspect-tools-decision ACTUAL_TOOLS_INPUT.json ROOT/event-configurations/UNUSED_TOOLS_BODY
    /usr/bin/python3 -I -B CLI issue-tools-decision ACTUAL_TOOLS_INPUT.json ROOT/event-configurations/UNUSED_TOOLS_BODY

Input schema dg16.g1-root-tools-decision-input.v1 has exactly artifact_session,
issued_unix_ms, expires_unix_ms plus schema. No G3 judgment is generated.

Tools/G3 publication preconfiguration keeps the exact decision-file boundary:

    /usr/bin/python3 -I -B CLI inspect-control ACTUAL_CONTROL_INPUT.json ROOT/event-configurations/UNUSED_CONTROL
    /usr/bin/python3 -I -B CLI issue-control ACTUAL_CONTROL_INPUT.json ROOT/event-configurations/UNUSED_CONTROL

Control input schema dg16.g1-root-control-issuance-input.v1 has exactly schema,
artifact_session, decision{path,sha256}, parent_sha, parent_ref_result{path,sha256},
window_opened_unix_ms, deadline_unix_ms, shell_title, initial_session,
initial_body and initial_publication. Initial values are null outside final G3.
Final binds actual initial Session/body and its published receive_control receipt.

The exact v5 peer adapter is installed on the immutable receiver namespace for
control planning. It selects github_fetch_file at the actual newly published
commit with encoding base64, preserving original wrappers and exact decoded
length/SHA256/Gitblob identity. No Git Data envelope or provider identity is
synthesized. Existing ref/commit/sole-parent/tree/closing semantics remain.

Output CONTROL_CONFIGURATION/CONTROL_ADMISSION are v2, and the canonical
TRUSTED_PUBLICATION_PLAN.json plus descriptor is emitted outside TTY. Pass those
actual bytes/hash to the pinned v6 runControlWithSelection API with received
WindowsRoleIO and940f5b… SHA helper; include the real github_fetch_file native
function. Do not use the prior v1 grant or a TTY-derived trusted plan.

All size/freshness/exclusive0600/fsync/readback/original-expiry guards from the
predecessor remain. Root prepares canonical owned parents under ROOT/sessions,
ROOT/control-sessions and ROOT/event-configurations. Only exit0 plus final
ISSUANCE_COMMITTED/ISSUANCE_READBACK permits use; partial writes are not retried
blindly. G3 original decisions and authentic independent/source-applicability
review remain Root/actual_packet.py duties, not JSON-label authority.

Verification:30 effect-free real-owner Python controls and six pure frozen-v6
trusted-plan controls. They cover all six status phases, current job/artifact
joins, historical queued publication status, wrong parent/job/artifact and
future cutoff refusal, exact v2 admission/peer pins and immutable file reads.
No actual grant or episode was exercised.
