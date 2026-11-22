"""Source-level tests of the policy-v3 Stop patch (repo SelectedStopDiagnosticsTests pattern).
Run from a repository checkout with stop-v3-and-activation.diff applied:
  python -m unittest path/to/test_stop_v3.py   (set IA_ROOT to the checkout root)
"""
import contextlib, hashlib, importlib.util, io, json, os, subprocess, sys, tempfile, types, unittest
from pathlib import Path
from unittest import mock

SRC = Path(os.environ.get("IA_ROOT", ".")) / "skills/implementaudit/scripts/host-stop-interlock.py"


def load():
    spec = importlib.util.spec_from_file_location("stop_v3", SRC)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def run(state, policy_kind):
    """state: 'none' | 'handoff' | 'closure' | 'both'. The owner seam mirrors validate-run-root.sh:258-263."""
    stop = load()
    with tempfile.TemporaryDirectory(prefix="v3-") as name:
        root = Path(name).resolve(); evidence, run_root, store = root / "e", root / "r", root / "s"
        for p in (evidence, run_root, store): p.mkdir()
        for n in ("validator.sh", "binding.py"): (root / n).write_text("#\n")
        packet = run_root / "HANDOFF.md"; packet.write_text("AUDIT_HANDOFF\n")
        closure = run_root / "CLOSURE.md"; closure.write_text("AUDIT_COMPLETE\n")
        pin = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        bound = dict(explicit_run_root=str(run_root))
        base = dict(session_id="sel", evidence_directory=str(evidence), cwd=str(root), binding_store=str(store),
                    binding_owner=str(root / "binding.py"), binding_owner_sha256="0" * 64, binding=bound,
                    validator=str(root / "validator.sh"), bash="bash")
        if policy_kind == "v1":
            policy = dict(base, schema="implementaudit.codex-stop-policy.v1")
        else:
            policy = dict(base, schema="implementaudit.codex-stop-policy.v3", dispositions=[
                {"kind": "NONTERMINAL_YIELD"},
                {"kind": "AUDITED_HANDOFF", "record": str(packet), "sha256": pin(packet)},
                {"kind": "TERMINAL_CLOSURE", "record": str(closure), "sha256": pin(closure)}])
        raw = json.dumps(policy).encode(); path = root / "policy.json"; path.write_bytes(raw)
        event = dict(session_id="sel", turn_id="t", hook_event_name="Stop", stop_hook_active=False,
                     last_assistant_message="x", cwd=str(root))
        terminal, handoff = state in ("closure", "both"), state in ("handoff", "both")

        def owner(policy, run_root, helper, custody, response, kind, record_binding):
            ok = (not (terminal and handoff)) and (
                (kind == "NONTERMINAL_YIELD" and not terminal and not handoff) or
                (kind == "TERMINAL_CLOSURE" and terminal and not handoff) or
                (kind == "AUDITED_HANDOFF" and handoff and not terminal))
            return subprocess.CompletedProcess([], 0 if ok else 1, json.dumps({"record_disposition": kind}) + "\n" if ok else "", "" if ok else "refused")

        os_proxy = types.SimpleNamespace(**{k: getattr(os, k) for k in dir(os) if k != "name"}, name="nt")
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(event).encode()))
        sys_proxy = types.SimpleNamespace(**{k: getattr(sys, k) for k in dir(sys) if k not in ("flags", "stdin")},
                                          flags=types.SimpleNamespace(isolated=True, no_site=True, dont_write_bytecode=True), stdin=stdin)
        looked = subprocess.CompletedProcess([], 0, json.dumps(dict(status="BOUND", binding=bound)) + "\n", "")
        with mock.patch.object(stop, "sys", sys_proxy), mock.patch.object(stop, "os", os_proxy), \
             mock.patch.object(stop, "load_pinned_owner", return_value=object()), \
             mock.patch.object(stop, "run_owner_module", return_value=looked), \
             mock.patch.object(stop, "selected_record_verdict", side_effect=owner), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            stop.selected_codex_stop(path, hashlib.sha256(raw).hexdigest())
        return json.loads(out.getvalue())


class V3(unittest.TestCase):
    def test_handoff_allowed_under_v3(self):
        self.assertIn("AUDITED_HANDOFF", run("handoff", "v3").get("systemMessage", ""))

    def test_yield_allowed_under_v3(self):
        self.assertIn("NONTERMINAL_YIELD", run("none", "v3").get("systemMessage", ""))

    def test_closure_allowed_under_v3(self):
        self.assertIn("TERMINAL_CLOSURE", run("closure", "v3").get("systemMessage", ""))

    def test_conflicting_claims_block(self):
        self.assertEqual(run("both", "v3").get("decision"), "block")

    def test_v1_still_blocks_handoff(self):        # unchanged legacy behaviour
        self.assertEqual(run("handoff", "v1").get("decision"), "block")


if __name__ == "__main__":
    unittest.main()
