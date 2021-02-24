from typing import List
from itertools import combinations
import collections


class Proposition:
    def __init__(self, interpretation: bool, name: str):
        self._interpretation = interpretation
        self._name = name

    def __bool__(self):
        return self._interpretation

    def __eq__(self, other):
        return self._interpretation == bool(other)

    def __hash__(self):
        return hash((self.name, self.interpretation))

    @property
    def interpretation(self) -> bool:
        return self._interpretation

    @property
    def name(self) -> str:
        return self._name


class Negation(Proposition):
    def __init__(self, a: Proposition):
        interpretation: bool = not a.interpretation
        super().__init__(interpretation, a.name)


class And(Proposition):
    def __init__(self, a: Proposition, b: Proposition):
        interpretation: bool = True if a and b else False
        super().__init__(interpretation, '%s_and_%s' % (a.name, b.name))


class Or(Proposition):
    def __init__(self, a: Proposition, b: Proposition):
        interpretation: bool = True if a or b else False
        super().__init__(interpretation, '%s_or_%s' % (a.name, b.name))


class Equivalence(Proposition):
    def __init__(self, a: Proposition, b: Proposition):
        interpretation: bool = (a == b)
        super().__init__(interpretation, '%s_eq_%s' % (a.name, b.name))


class Tautology(Proposition):
    def __init__(self, a_list=List[Proposition]):
        interpretation: bool = any(a_list)  # Not sure whether this is correct
        super().__init__(interpretation, 'tautology')


class Case(Proposition):
    def __init__(self, fact_set: List[Proposition], value: int, name: str):
        self._fact_set = fact_set
        self._value = value
        interpretation = all(self._fact_set)
        super().__init__(interpretation, name)

    @property
    def fact_set(self):
        return self._fact_set

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return collections.Counter(self._fact_set) == collections.Counter(other.fact_set)


class CaseModel:
    def __init__(self, cases: List[Case]):
        self._cases: List[Case] = cases
        self._valid = False
        self._check_validity()

    def _check_validity(self):
        # Definition 1, page 131
        # ToDo: Implement condition 1 and 5
        for case1, case2 in combinations(self._cases, 2):
            if not Equivalence(case1, case2):
                assert Negation(And(case1, case2)), "Case Model not valid, condition 2 was violated"
            if Equivalence(case1, case2):
                assert case1 == case2, "Case Model not valid, condition 3 was violated"
            if not (case1.value >= case2.value or case1.value <= case2.value):
                assert False, "Case Model not valid, condition 4 was violated"

        self._valid = True

    @property
    def cases(self):
        return self._cases

    @property
    def valid(self):
        return self._valid
