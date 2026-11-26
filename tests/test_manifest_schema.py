"""manifest.json holds to manifest.schema.json, and tools/describe.py writes every corpus entry in that shape. Standard
library only (the subset of JSON Schema the schema uses is checked here); needs no corpus checked out.

  python -m unittest tests.test_manifest_schema -v
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import describe  # noqa: E402

SCHEMA = json.loads((ROOT / 'manifest.schema.json').read_text(encoding='utf-8'))
TYPES = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'number': (int, float)}


def problems(value, schema: dict, where: str = '$') -> list[str]:
    """Where `value` breaks `schema`: the keywords manifest.schema.json uses ($ref to #/$defs, type, enum, pattern,
    minimum, required, properties, additionalProperties: false, items)."""
    if '$ref' in schema:
        schema = {**SCHEMA['$defs'][schema['$ref'].rsplit('/', 1)[1]], **{k: v for k, v in schema.items() if k != '$ref'}}
    if 'type' in schema:
        want = TYPES[schema['type']]
        if not isinstance(value, want) or (schema['type'] in ('integer', 'number') and isinstance(value, bool)):
            return [f'{where}: {type(value).__name__}, not {schema["type"]}']
    out = []
    if 'enum' in schema and value not in schema['enum']:
        out.append(f'{where}: {value!r} is none of {schema["enum"]}')
    if 'pattern' in schema and isinstance(value, str) and not re.search(schema['pattern'], value):
        out.append(f'{where}: {value!r} does not match {schema["pattern"]}')
    if 'minimum' in schema and isinstance(value, (int, float)) and value < schema['minimum']:
        out.append(f'{where}: {value} is below {schema["minimum"]}')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        out += [f'{where}: no {k}' for k in schema.get('required', []) if k not in value]
        if schema.get('additionalProperties') is False:
            out += [f'{where}: {k} is not in manifest.schema.json' for k in value if k not in props]
        for k, v in value.items():
            if k in props:
                out += problems(v, props[k], f'{where}.{k}')
    if isinstance(value, list) and 'items' in schema:
        for i, v in enumerate(value):
            out += problems(v, schema['items'], f'{where}[{i}]')
    return out


class Schema(unittest.TestCase):
    def test_the_manifest_holds_to_its_schema(self):
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        found = problems(manifest, SCHEMA)
        # one line per corpus at most, so a failure names each corpus once
        self.assertEqual(found, [], f'{len(found)} problem(s), the first: ' + '; '.join(found[:15]))

    def test_one_entry_per_path(self):
        corpora = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']
        paths = [c['path'] for c in corpora]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(paths, sorted(paths), 'describe.py writes the corpora sorted by path')

    def test_every_key_describe_copies_is_in_the_schema(self):
        allowed = set(SCHEMA['$defs']['corpus']['properties'])
        self.assertEqual(sorted(set(describe.CORPUS_KEYS) - allowed), [])

    def test_the_checker_finds_what_it_should(self):
        corpus = SCHEMA['$defs']['corpus']
        good = {'path': 'germany/bund/acts', 'url': 'https://github.com/lexifina/germany-law.git',
                'iso_path': 'de/bund/acts', 'in_force_trailer': 'In-force', 'described_by': 'corpus.json',
                'kind': 'legislation', 'acts': 3}
        self.assertEqual(problems(good, corpus), [])
        self.assertTrue(problems({**good, 'acts': ['a', 'b']}, corpus))
        self.assertTrue(problems({**good, 'acts': True}, corpus))
        self.assertTrue(problems({**good, 'kind': 'statutes'}, corpus))
        self.assertTrue(problems({**good, 'has_future_branch': True}, corpus))
        self.assertTrue(problems({k: v for k, v in good.items() if k != 'kind'}, corpus))
        self.assertTrue(problems({**good, 'record_to': '2026-1-5'}, corpus))


class Normalise(unittest.TestCase):
    def test_an_act_list_becomes_its_count(self):
        self.assertEqual(describe.normalise({'path': 'japan/national/acts', 'acts': ['a', 'b', 'c']})['acts'], 3)
        self.assertEqual(describe.normalise({'path': 'x/national/acts', 'acts': {'a': 1, 'b': 2}})['acts'], 2)
        self.assertEqual(describe.normalise({'path': 'x/national/acts', 'acts': 7})['acts'], 7)
        self.assertNotIn('acts', describe.normalise({'path': 'x/national/acts', 'acts': 'many'}))

    def test_every_entry_has_a_kind(self):
        self.assertEqual(describe.normalise({'path': 'x/national/acts'})['kind'], 'legislation')
        self.assertEqual(describe.normalise({'path': 'x/national/caselaw'})['kind'], 'judgments')
        self.assertEqual(describe.normalise({'path': 'x/national/acts', 'kind': 'Court'})['kind'], 'judgments')
        self.assertEqual(describe.normalise({'path': 'us/federal/irs-guidance', 'kind': 'guidance'})['kind'], 'guidance')

    def test_a_plain_scope_is_the_selection(self):
        e = describe.normalise({'path': 'x/national/acts', 'scope': 'selected-acts'})
        self.assertEqual((e.get('selection'), 'scope' in e), ('selected-acts', False))
        applies = {'trailer': 'Applies'}
        self.assertEqual(describe.normalise({'path': 'x/national/acts', 'scope': applies})['scope'], applies)

    def test_leftover_keys_go(self):
        self.assertNotIn('has_future_branch', describe.normalise({'path': 'x/national/acts', 'has_future_branch': True}))

    def test_normalising_twice_changes_nothing(self):
        once = describe.normalise({'path': 'x/national/acts', 'acts': ['a'], 'scope': 'all-acts', 'kind': 'decisions'})
        self.assertEqual(describe.normalise(dict(once)), once)


if __name__ == '__main__':
    unittest.main()
