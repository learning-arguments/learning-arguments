from logic import *
import unittest


def test_1():
    rain = Fact('rain')
    sun = Fact('sun')
    not_sun = Fact('sun', False)

    case1 = Case([not_sun, rain], probability=0.5, name='case1')
    case2 = Case([sun], probability=0.5, name='case2')

    case_model = CaseModel(cases=[case1, case2])

    argument = Argument(premise=rain, conclusion=not_sun)
    print('%s is coherent: %s' % (argument, case_model.coherent(argument)))
    print('%s is conclusive: %s' % (argument, case_model.conclusive(argument)))

    return case_model.valid


def test_simonshaven():
    guilty = Fact('guilty')
    robbery = Fact('robbery')
    perry = Fact('Perry')
    third = Fact('third')
    all_evidence = Fact('all evidence')

    not_guilty = Fact('guilty', False)
    not_robbery = Fact('robbery', False)
    not_perry = Fact('Perry', False)
    not_all_evidence = Fact('all evidence', False)

    case1 = Case([guilty, all_evidence], probability=0.5, name='case 1')
    case2_a = Case([guilty, robbery, perry, not_all_evidence], probability=0.2, name='case 2_a')
    case2_b = Case([not_guilty, robbery, not_perry, third, not_all_evidence], probability=0.2,
                   name='case2_b')
    case3 = Case([not_guilty, not_robbery, not_all_evidence], probability=0.1, name='case 3')

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
