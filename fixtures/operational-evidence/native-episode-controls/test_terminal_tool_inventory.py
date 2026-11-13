"""Source-only terminal inventory controls; no native authority is constructed."""
import copy
import unittest

from native_test_support import load
import test_native_startup_envelopes as startup


class TerminalToolInventoryControls(unittest.TestCase):
    def setUp(self):
        self.fixture = startup.NativeStartupEnvelopeControls()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.obs = self.fixture.obs
        self.owner = load('compaction-source-owner-codex-app.py')

    def inventory(self, *, declaration=True, version='0.164.0-alpha.11.1'):
        invoke, fixture, rows, labels, context = self.fixture.episode(
            declaration=declaration, version=version)
        invoke()  # Same declaration must first pass the real HOLD consumer.
        records, _ = self.obs.hold_records(context)
        # The fixture ends at its pending BIND call. Complete that source-only
        # call explicitly for the terminal-inventory unit; no native event claim.
        call = records[-1]['row']['payload']
        records.append({'row': {'type': 'response_item', 'payload': {
            'type': 'custom_tool_call_output', 'call_id': call['call_id']}},
            'locator': {'offset': fixture['bytes'], 'bytes': 1}})
        return records, context, fixture['selectors'][labels['load_call']]['offset']

    def test_same_admitted_declaration_reaches_terminal_inventory(self):
        records, context, load_offset = self.inventory()
        actual = self.owner.tool_calls(self.obs, records, context, load_offset)
        without = [r for r in records if r['row'].get('payload', {}).get('type') != 'additional_tools']
        self.assertEqual(actual, self.owner.tool_calls(self.obs, without))

    def test_terminal_declaration_retains_profile_and_closed_preload_shape(self):
        records, context, load_offset = self.inventory()
        index = next(i for i, r in enumerate(records) if r['row'].get('payload', {}).get('type') == 'additional_tools')
        for mutation in ('role', 'extra', 'provenance', 'late', 'unknown', 'profile', 'no-context'):
            with self.subTest(mutation=mutation):
                selected, ctx = copy.deepcopy(records), copy.deepcopy(context)
                row = selected[index]['row']
                if mutation == 'role': row['payload']['role'] = 'assistant'
                elif mutation == 'extra': row['payload']['command'] = 'not-inert'
                elif mutation == 'provenance': row['metadata']['client_authored'] = 0
                elif mutation == 'late': selected[index]['locator']['offset'] = load_offset
                elif mutation == 'unknown': row['payload']['type'] = 'unclassified_effect'
                elif mutation == 'profile': ctx['profile_id'] = self.obs.OWNED_STDIO_PROFILE
                elif mutation == 'no-context': ctx = None
                with self.assertRaisesRegex(ValueError, 'SOURCE_OWNER_(UNQUALIFIED_TOOL_DECLARATION|UNCLASSIFIED_EFFECT_ROW)'):
                    self.owner.tool_calls(self.obs, selected, ctx, load_offset)

    def test_declaration_never_hides_unsettled_or_duplicate_calls(self):
        records, context, load_offset = self.inventory()
        with self.assertRaisesRegex(ValueError, 'SOURCE_OWNER_UNSETTLED_EFFECT_CALL'):
            self.owner.tool_calls(self.obs, records[:-1], context, load_offset)
        duplicate = copy.deepcopy(records)
        duplicate.append(copy.deepcopy(records[-1]))
        with self.assertRaisesRegex(ValueError, 'SOURCE_OWNER_EFFECT_OUTPUT_ASSOCIATION'):
            self.owner.tool_calls(self.obs, duplicate, context, load_offset)
        changed = copy.deepcopy(records)
        call = next(r for r in changed if r['row'].get('payload', {}).get('type') == 'custom_tool_call')
        call['row']['payload']['input'] += ' changed actual effect'
        self.assertNotEqual(self.owner.tool_calls(self.obs, changed, context, load_offset),
                            self.owner.tool_calls(self.obs, records, context, load_offset))
