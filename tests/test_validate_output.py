import copy
import json
import os
import unittest

from tests.helpers import CASE1, ROOT, load_case
from validate_output import validate

SCHEMA = json.load(open(os.path.join(ROOT, 'shared', 'references', 'output-schema.json')))


class SchemaTest(unittest.TestCase):
    def setUp(self):
        _, self.output, _ = load_case(CASE1)

    def test_reference_output_valid(self):
        self.assertEqual(validate(self.output, SCHEMA), [])

    def test_missing_section(self):
        o = copy.deepcopy(self.output)
        del o['analysis']
        self.assertIn('$: missing required "analysis"', validate(o, SCHEMA))

    def test_stage_outputs_valid(self):
        # Staged workflow: a fit check holds only the analysis; a CV rewrite adds the CV.
        o = copy.deepcopy(self.output)
        for key in ('cover_letter', 'interview', 'cv'):
            o.pop(key, None)
            self.assertEqual(validate(o, SCHEMA), [], key)

    def test_bad_enum_and_range(self):
        o = copy.deepcopy(self.output)
        o['analysis']['verdict'] = 'maybe'
        o['analysis']['match_score'] = 140
        errors = ' '.join(validate(o, SCHEMA))
        self.assertIn('verdict', errors)
        self.assertIn('above 100', errors)

    def test_wrong_type(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['bullets'][0] = 'plain string'
        self.assertTrue(any('expected object' in e for e in validate(o, SCHEMA)))

    def test_boolean_is_not_integer(self):
        o = copy.deepcopy(self.output)
        o['analysis']['match_score'] = True
        self.assertTrue(validate(o, SCHEMA))


if __name__ == '__main__':
    unittest.main()
