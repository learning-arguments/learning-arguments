from typing import List
from itertools import combinations
import collections


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
    def __init__(self, premise: Fact, conclusion: Fact):
        self._premise = premise
        self._conclusion = conclusion

    def __str__(self):
        return 'if %s then %s' % (self._premise.statement, self._conclusion.statement)

    @property
    def conclusion(self):
        return self._conclusion

    @property
    def premise(self):
        return self._premise


class Case:
    def __init__(self, fact_set: List[Fact], probability=0.0, name: str = None):
        self._fact_set = fact_set
        self._value = probability
        self._name = name

    @property
    def fact_set(self):
        return self._fact_set

    @property
    def probability(self):
        return self._value

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return collections.Counter(self._fact_set) == collections.Counter(other.fact_set)

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
        self._check_validity()

    def _check_validity(self):
        # Definition 1, page 131
        # ToDo: Implement condition 5
        for case1, case2 in combinations(self._case_list, 2):
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
    def cases(self):
        return self._case_list

    @property
    def valid(self):
        return self._valid

    def coherent(self, arg: Argument):
        for case in self._case_list:
            if arg.premise in case.fact_set and arg.conclusion in case.fact_set and case.probability > 0.0:
                return True
        return False

    def conclusive(self, arg):
        if self.coherent(arg):
            for case in self._case_list:
                if not (case.probability > 0.0 and arg.premise in case.fact_set and arg.conclusion in case.fact_set):
                    return False
                else:
                    return True


def conditional_probability(case1: Case, case2: Case):
    if case2.probability != 0.0:
        return (case1.probability + case2.probability) / case2.probability
