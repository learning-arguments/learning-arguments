from logic import *
import unittest


def test_1():
    rain = Proposition(True, 'rain')
    sun = Proposition(True, 'sun')

    case1 = Case([Negation(sun), rain], value=1, name='case1')
    case2 = Case([sun, Negation(rain)], value=2, name='case2')

    case_model = CaseModel(cases=[case1, case2])
    return case_model.valid


def test_simonshaven():
    guilty = Proposition(True, 'guilty')
    robbery = Proposition(True, 'robbery')
    perry = Proposition(True, 'Perry')
    third = Proposition(True, 'third')
    all_evidence = Proposition(True, 'all evidence')

    case1 = Case([guilty, all_evidence], value=0.5, name='case 1')
    case2_a = Case([Negation(guilty), robbery, perry, Negation(all_evidence)], value=0.2, name='case 2_a')
    case2_b = Case([Negation(guilty), robbery, Negation(perry), third, Negation(all_evidence)], value=0.2, name='case2_b')
    case3 = Case([Negation(guilty), Negation(robbery), Negation(all_evidence)], value=0.1, name='case 3')

    case_model = CaseModel(cases=[case1, case2_a, case2_b, case3])
    return case_model.valid

class TestStringMethods(unittest.TestCase):
    # https://docs.python.org/3/library/unittest.html
    # functions in here have to start with 'test'
    def test_case_model_creation(self):
        self.assertTrue(test_1())

    def test_case_model_simonshaven(self):
        self.assertTrue(test_simonshaven())


if __name__ == "__main__":
    unittest.main()
