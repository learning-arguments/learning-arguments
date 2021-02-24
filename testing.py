from logic import *
import unittest


def test_1():
    rain = Proposition(True, 'rain')
    sun = Proposition(True, 'sun')

    case1 = Case([Negation(sun), rain], value=1, name='case1')
    case2 = Case([sun, Negation(rain)], value=2, name='case2')

    case_model = CaseModel(cases=[case1, case2])
    return case_model.valid


class TestStringMethods(unittest.TestCase):
    # https://docs.python.org/3/library/unittest.html
    # functions in here have to start with 'test'
    def test_case_model_creation(self):
        self.assertTrue(test_1())


if __name__ == "__main__":
    unittest.main()
