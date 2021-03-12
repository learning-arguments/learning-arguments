from typing import List
from itertools import combinations
from collections import Counter


class Fact:
    def __init__(self, statement: str, not_negated: bool = True):
        self._statement = statement if not_negated else 'not %s' % statement
        self._not_negated = not_negated

    def __eq__(self, other):
        return (self._statement == other.statement) and (self._not_negated == other.not_negated)

    def __hash__(self):
        return hash((self.statement, self._not_negated))

    def __bool__(self):
        return self._not_negated

    @property
    def statement(self) -> str:
        return self._statement

    @property
    def not_negated(self) -> bool:
        return self._not_negated


class Negation(Fact):
    def __init__(self, a: Fact):
        truth_value: bool = not a.not_negated
        statement = 'not %s' % a.statement
        super().__init__(statement, truth_value)


class And(Fact):
    def __init__(self, a: Fact, b: Fact):
        truth_value: bool = True if a and b else False
        statement = '%s and %s' % (a.statement, b.statement)
        super().__init__(statement, truth_value)


class Or(Fact):
    def __init__(self, a: Fact, b: Fact):
        truth_value: bool = True if a or b else False
        statement = '%s or %s' % (a.statement, b.statement)
        super().__init__(statement, truth_value)


class Equivalence(Fact):
    def __init__(self, a: Fact, b: Fact):
        truth_value: bool = (a == b)
        statement = '%s is equivalent to %s' % (a.statement, b.statement)
        super().__init__(statement, truth_value)


class Tautology(Fact):
    def __init__(self, a_list=List[Fact]):
        truth_value: bool = any(a_list)  # Not sure whether this is correct
        statement = 'tautology'
        super().__init__(statement, truth_value)


class Argument:
    # An argument from 'P to not Q' makes the case 'P and not Q'
    # see Definition 2, page 132
    def __init__(self, premises: List[Fact], conclusion: Fact):
        self._premises = premises
        self._conclusion = conclusion

    def __str__(self):
        return_string = ''
        for fact in self._premises[:-1]:
            return_string += 'if %s and' % fact.statement
        return_string += 'if %s' % self._premises[-1]
        return_string += 'than %s' % self._conclusion.statement
        return return_string

    @property
    def conclusion(self) -> Fact:
        return self._conclusion

    @property
    def premises(self) -> list:
        return self._premises


class Case:
    def __init__(self, fact_set: List[Fact], probability=0.0, name: str = None):
        self._fact_set = fact_set
        self._probability = probability
        self._name = name

    @property
    def fact_set(self) -> list:
        return self._fact_set

    @property
    def probability(self) -> float:
        return self._probability

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other):
        return Counter(self._fact_set) == Counter(other.fact_set)

    def __add__(self, other):
        return Case(self._fact_set + other.fact_set,
                    self.probability + other.probability,
                    self.name + ' and ' + other.name)

    def negate(self):
        negated_fact_set = [Fact(f.statement, not f.not_negated) for f in self._fact_set]
        return Case(fact_set=negated_fact_set, probability=self.probability, name=self.name)


class CaseModel:
    def __init__(self, cases: List[Case]):
        self._case_list: List[Case] = cases
        self._valid = False

    def check_validity(self, print_progress: bool = False):
        # Definition 1, page 131
        # ToDo: Implement condition 5
        for case1, case2 in combinations(self._case_list, 2):
            if print_progress:
                print('Check validity %s %s ' % (case1.name, case2.name))
            assert case1.negate() not in self._case_list, "Case Model not valid, condition 1 was violated"
            if not case1 == case2:
                assert not case1 + case2 in self._case_list, "Case Model not valid, condition 2 was violated"
            if case1 == case2:
                assert case1 == case2, "Case Model not valid, condition 3 was violated"
                # This is trivial
            if not (case1.probability >= case2.probability or case1.probability <= case2.probability):
                assert False, "Case Model not valid, condition 4 was violated"

        self._valid = True

    @property
    def cases(self) -> list:
        return self._case_list

    @property
    def valid(self) -> bool:
        return self._valid

    def coherent(self, arg: Argument) -> (bool, Case):
        for case in self._case_list:
            if all([fact in case.fact_set for fact in arg.premises]) and \
                    arg.conclusion in case.fact_set and \
                    case.probability > 0.0:
                return True, case
        return False, None

    def conclusive(self, arg: Argument) -> bool:
        coherent, coherent_case = self.coherent(arg)
        if coherent:
            for case in self._case_list:
                if not (all([fact in case.fact_set for fact in arg.premises]) and
                        arg.conclusion in case.fact_set and
                        case.probability > 0.0):
                    return False
            return True

    def presumptively_valid(self, arg: Argument) -> bool:
        coherent, coherent_case = self.coherent(arg)
        if coherent:
            for case in self._case_list:
                if all([fact in case.fact_set for fact in arg.premises]):
                    if not coherent_case.probability >= case.probability:
                        return False
            return True

    def probability(self, fact: Fact) -> float:
        probability = 0.0
        for case in self._case_list:
            if fact in case.fact_set:
                probability += case.probability
        return probability

    def conditional_probability(self, fact: Fact, given_fact: Fact) -> float:
        probability = 0.0
        for case in self._case_list:
            if fact in case.fact_set and given_fact in case.fact_set:
                probability += case.probability
        return probability / self.probability(given_fact)
