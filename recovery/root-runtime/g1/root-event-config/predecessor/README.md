G1 Root event issuance CLI is `g1_event_config.py`. It uses the received
receiver-02, installed role_v4/control_v3, and FINAL_CALLBACK_HANDOFF's exact
callback pins. This task executed no issue-* command and issued no grant,
configuration, tools adoption, G3 decision, control publication or host effect.

The required workflow commit is f9ba187e8f5520956f0f16cf13c0a706e8360b96,
branch pro/dg16-g1-original-g3-04-20261109. This is the approved local job
subject, not a numeric provider job ID. Actual run_id, source/provider receiving,
existing deadlines, current ref parent and semantic decisions must come later.

`INPUT_CONTRACTS.json` defines the exact input files. All descriptor rows are
exactly {path,sha256}; original complete bytes are bounded and rehashed. The
four provider results are authentic Root-supported run/attempt/jobs/workflow
wrappers plus their actual safe native/provider receiving. Existing receiver
functions check the workflow, commit, same run/attempt/job, status and chronology.
Root authenticates native provenance separately; matching JSON is not authority.

Invoke the source through Root's received hash-checking loader or install the
exact reviewed CLI as immutable Root-owned source. Commands run on existing
Ubuntu/agent with installed receiver-02. For example, CLI may be the exact
reviewed Windows source mapped read-only into WSL, or its verified installed
copy. ROOT below is:

    /home/agent/dg16-g1-current04-operators/public-receiver-02

First inspect a genuine event without issuing or writing anything:

    /usr/bin/python3 -I -B CLI inspect-role ACTUAL_ROLE_INPUT.json ROOT/event-configurations/UNUSED_NAME

Only the actual native Root may subsequently invoke:

    /usr/bin/python3 -I -B CLI issue-role ACTUAL_ROLE_INPUT.json ROOT/event-configurations/UNUSED_NAME

The input selects tools, recipient, g3_initial, g3_final, terminal or failure.
For final G3 receiving, the actual initial Session and exact original first
Root-decision bytes are reconstructed/validated first. Other phases reject
unrelated initial inputs. The original window is never reset or extended.

Outputs are canonical, size-checked CONTEXT, ROLE_ADMISSION,
ROLE_CONFIGURATION, Windows selection and provider-binding descriptors. Paths
match role_v4 exactly and target a fresh receiver Session. Output directories
must already have a canonical parent under ROOT/event-configurations; Root
must create that parent once with correct owned0700 custody before issuance.
ROOT/sessions and ROOT/control-sessions parents must likewise exist before the
actual role/control starts. The CLI does not create a native Session.

After a genuine successful tools Session, Root may construct its exact adoption
body from the real requirements and explicitly supplied issuance/expiry:

    /usr/bin/python3 -I -B CLI inspect-tools-decision ACTUAL_TOOLS_INPUT.json ROOT/event-configurations/UNUSED_TOOLS_BODY
    /usr/bin/python3 -I -B CLI issue-tools-decision ACTUAL_TOOLS_INPUT.json ROOT/event-configurations/UNUSED_TOOLS_BODY

That input schema is dg16.g1-root-tools-decision-input.v1 with exactly
artifact_session, issued_unix_ms and expires_unix_ms in addition to schema.
Only the real requirements' fixed fields are used; existing validate_control
must accept the body. This command does not construct any G3 judgments.

For tools or either G3 control, consume the exact Root-issued DECISION.json,
actual successful artifact Session, and fresh complete current-parent ref result:

    /usr/bin/python3 -I -B CLI inspect-control ACTUAL_CONTROL_INPUT.json ROOT/event-configurations/UNUSED_CONTROL
    /usr/bin/python3 -I -B CLI issue-control ACTUAL_CONTROL_INPUT.json ROOT/event-configurations/UNUSED_CONTROL

Final control additionally requires the actual first Session, original first
decision, and receive_control publication receipt proving the initial published
commit is the current parent. Existing receiver Session/requirements/
validate_control/publication_plan functions reconstruct and validate the whole
join. Parent wrappers pass the pinned control_v3 credential guard. No row,
independent review digest, current parent or issuer body is manufactured.

The control output includes exact control_v3 configuration/admission plus the
canonical TRUSTED_PUBLICATION_PLAN.json and its descriptor. The plan is built
outside the TTY. Its full bytes/hash are the trusted callback input; the grant's
plan_contract hash excludes only root_body_validation_at_unix_ms, matching the
unchanged control_v3 owner. Callback-plan limit262144, config/admission65536,
decision16384 and original first-decision8192 are enforced before writing.

Every issue output is fresh/exclusive owned0600 with fsync/readback. Only after
all files and ISSUANCE_READBACK.json match is zero-byte ISSUANCE_COMMITTED
published and the directory fsynced. Use outputs only after exit0 and that
committed readback. Partial/unknown issuance is not usable and is not overwritten
or retried blindly. Inspect output descriptors alone are not issued bodies.

For artifact roles, pass the issued Windows selection to the exact received
WindowsRoleIO0bfbe734... and seven-slot3b92c9b5... callbacks, using real Root
tools and the unchanged existing expiry. For controls, the frozen API is:

    runControlWithSelection(tools, native, issuedWindowsSelection,
      originalDeadline, receivedWindowsRoleIO,
      actualTrustedPlanRaw, actualTrustedPlanSHA, received940SHA256)

Control callback is94e1f736..., role iscd9e9f34..., control driver isc381d6fa....
All exact source descriptors are in SOURCE_INPUTS.json/FINAL_CALLBACK_HANDOFF.
Do not use an older callback or infer trusted plan bytes from TTY narration.
Actual parent/native calls and receipts remain Root-exclusive.

G3 decisions are coordinated with dg16_original_contract_receive. Initial
decision consumes the two component returns with zero original awards; it does
not demand original-row acceptance. Final original rows remain ordered by the
real G.ORIGINAL_IDS and validated by the original owner. L04 retains its natural
RLGWO residual; L07 retains global-liveness and retirement/transfer residuals.
This current04 subject cannot grant full G3 acceptance. Actual independent live
review and source-applicability digests are genuine Root inputs, never defaults.

The adjacent `../root-live-g3/actual_packet.py` (SHA256
a12cdc5581a8b1add2b6ac82ed04ca626335388f44fc4e0baf66f50634b769ae)
provides `inspect --session ...` and `check-body --session ... --body ...
--independent-review ...`; final intake also binds initial Session/body and
actual source-applicability review. It is mechanical data-validation only,
not an independent semantic review or prior Root receiving. Its authentic
review/provider/source occurrence and Root authority remain external duties.

Verification:19 effect-free real-source Python checks and six pure frozen
callback trusted-plan checks pass. The tools artifact/adoption/plan and future
role documents used constructed data only. No native/provider tool call,
physical accepting role, actual grant or semantic original award is claimed.
The final disposition of this subtask is HOLD after delivery.
