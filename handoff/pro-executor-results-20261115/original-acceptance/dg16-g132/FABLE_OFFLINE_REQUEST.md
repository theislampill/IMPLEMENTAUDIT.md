## Fable local support: one G132 offline preflight

PRO-EXECUTOR-01 received the owner direction to send Fable one specific Windows/WSL operation. The exact fee1768b support and a33b8d1c host Git object have been received; recorded source qualifications are being reused.

Please run the existing offline preflight below once in the original Ubuntu WSL installation as `agent` on 3701Media. Return only its public stdout, stderr, exit code and elapsed time in the support branch or this conversation thread. The original R0035/#209 Q06, D05/D07 and L04 behavior remains required; this operation only receives the retained source inputs and measures the existing offline staging call.

Use the existing installed inputs. If any original input is absent, report the first missing input without reconstructing it. This request authorizes no sender/provider/model operation, recipient/key or cryptographic operation, role/admission issuance, ref push, protected launch, or upload of retained private input bodies. The existing preflight stops before live Root bodies.

```bash
g132_timing=/home/agent/pro-executor-g132-offline-timing-20261115
mkdir -m 700 "$g132_timing" || exit 1
TIMEFORMAT='elapsed_seconds=%R'
{
  time /usr/bin/python3 -I -B \
    /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/late-assembler-01/assemble_actual.py \
    --stage /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/late-assembler-01/source-stage-01 \
    --host-phase /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/public-receiver-02/phase \
    --root-reader /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/public-receiver-02/author/receiver.py \
    --dispatcher-source /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/dispatcher-templates-02/bind_dispatcher.py \
    --private-inputs /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/retained-final5f-private-inputs \
    --preflight >"$g132_timing/stdout.txt" 2>"$g132_timing/stderr.txt"
} 2>"$g132_timing/timing.txt"
g132_status=$?
printf '%s\n' "$g132_status" >"$g132_timing/exit-code.txt"
exit "$g132_status"
```

Root's existing local `command assemble` generation ran once: exit0, 0.035seconds, `actual_execution:false`. This is not the full G132 chain or a substitute for G131's live Root-step timing. Correct live passthrough syntax remains `late-assemble -- --stage ...`. Do not run the emitted live command or any accepting operation under this offline request.
