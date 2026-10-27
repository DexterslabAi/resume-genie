import copy
import unittest

from tests.helpers import CASE1, CASE2, load_case
from check_fabrication import check


class FabricationTest(unittest.TestCase):
    def setUp(self):
        self.cv, self.output, self.notes = load_case(CASE1)

    def types(self, output, notes=''):
        return {i['type'] for i in check(self.cv, output, notes)['issues']}

    def test_reference_outputs_are_clean(self):
        for case in (CASE1, CASE2):
            cv, output, notes = load_case(case)
            r = check(cv, output, notes)
            self.assertTrue(r['clean'], r['issues'])
            self.assertGreater(r['placeholders'], 0)

    def test_derived_percentage_allowed(self):
        # "9 to 4 days (56% faster)" is arithmetic on the candidate's own numbers.
        self.assertIn('56%', self.output['cv']['experience'][0]['bullets'][0]['text'])
        self.assertTrue(check(self.cv, self.output)['clean'])

    def test_invented_number_caught(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['bullets'].append({'text': 'Managed a team of 14 analysts.'})
        self.assertIn('invented_number', self.types(o))

    def test_number_from_extra_facts_allowed(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['bullets'].append({'text': 'Managed a team of 14 analysts.'})
        self.assertNotIn('invented_number', self.types(o, notes='My team had 14 analysts.'))

    def test_placeholders_are_not_numbers(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['bullets'].append({'text': 'Saved [EUR 250k] a year.', 'needs_confirmation': True})
        self.assertTrue(check(self.cv, o)['clean'])

    def test_fake_employer_caught(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['company'] = 'Google'
        self.assertIn('unknown_employer', self.types(o))

    def test_employer_suffix_tolerated(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['company'] = 'Harbourline Group Ltd'
        self.assertNotIn('unknown_employer', self.types(o))

    def test_shifted_dates_caught(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['dates'] = '2019 - Present'
        self.assertIn('changed_date', self.types(o))

    def test_unflagged_placeholder_caught(self):
        o = copy.deepcopy(self.output)
        o['cv']['experience'][0]['bullets'][1]['needs_confirmation'] = False
        self.assertIn('unflagged_placeholder', self.types(o))


if __name__ == '__main__':
    unittest.main()
