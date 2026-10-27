import unittest

from tests.helpers import CASE1, load_case
from ats_score import _norm, ats_score, compare, contains_term, cv_to_text, format_checks, keyword_coverage


class MatchingTest(unittest.TestCase):
    def test_whole_terms_only(self):
        t = _norm('Built dashboards in Power BI; strong SQL.')
        self.assertTrue(contains_term(t, 'power bi'))
        self.assertTrue(contains_term(t, 'SQL'))
        self.assertFalse(contains_term(t, 'BI tools'))
        self.assertFalse(contains_term(_norm('Ruby on Rails'), 'R'))

    def test_plurals_and_stems(self):
        t = _norm('Created a dashboard and managed stakeholders')
        self.assertTrue(contains_term(t, 'dashboards'))
        self.assertTrue(contains_term(t, 'stakeholder'))

    def test_special_terms(self):
        t = _norm('Led SAP S/4HANA testing; wrote C++ and C#.')
        for term in ('SAP S/4HANA', 'C++', 'C#'):
            self.assertTrue(contains_term(t, term), term)

    def test_required_weighting_and_synonyms(self):
        r = keyword_coverage('Owned the purchase-to-pay process.', [
            {'term': 'P2P', 'importance': 'required', 'synonyms': ['purchase-to-pay']},
            {'term': 'Kubernetes', 'importance': 'preferred'},
        ])
        self.assertEqual(r['matched'], ['P2P'])
        self.assertEqual(r['score'], 67)  # 2 of 3 weighted points

    def test_duplicates_ignored(self):
        self.assertEqual(keyword_coverage('python', [{'term': 'Python'}, {'term': 'python'}])['score'], 100)


class ScoringTest(unittest.TestCase):
    def test_reference_scores_are_stable(self):
        cv, output, _ = load_case(CASE1)
        r = compare(cv, output)
        # Same numbers as the original JavaScript implementation: the score is reproducible.
        self.assertEqual((r['before']['score'], r['after']['score']), (57, 75))

    def test_format_checks(self):
        cv, _, _ = load_case(CASE1)
        checks = format_checks(cv)['checks']
        self.assertTrue(checks['email address present'])
        self.assertTrue(checks['experience heading'])
        self.assertFalse(checks['40%+ of bullets show a number'])  # the sample CV is weak on numbers

    def test_unusual_characters_flagged(self):
        self.assertFalse(format_checks('Hello ☀ world')['checks']['no unusual characters'])

    def test_cv_to_text_has_every_section(self):
        _, output, _ = load_case(CASE1)
        text = cv_to_text(output['cv'])
        for s in ('Professional Summary', 'Skills', 'Professional Experience', 'Education', 'Certifications', 'Harbourline Group'):
            self.assertIn(s, text)

    def test_empty_keywords(self):
        self.assertEqual(ats_score('anything', [])['keyword_score'], 0)


if __name__ == '__main__':
    unittest.main()
