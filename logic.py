from typing import List, FrozenSet, Optional, Union, Tuple, TypeVar, Iterable
from dataclasses import dataclass
from itertools import combinations
from multiprocessing import Pool
from re import split
from functools import cached_property


@dataclass(frozen=True)
class Fact:
    statement: str
    is_true: bool = True

    def __repr__(self) -> str:
        return ('' if self.is_true else '¬') + self.statement

    @property
    def negation(self) -> 'Fact':
        return Fact(self.statement, not self.is_true)

    @staticmethod
    def fromStr(str: str) -> 'Fact':
        if str[0] == '¬' or str[0] == '~':
            return Fact(str[1:], False)
        else:
            return Fact(str, True)


class Negation(Fact):
    def __init__(self, a: Fact):
        truth_value: bool = not a.is_true
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


def implies(a: bool, b: bool) -> bool:
    return (not a) or b

A = TypeVar('A')

def subset(a: Iterable[A], b: Iterable[A]) -> bool:
    return all([a_ in b for a_ in a])


def proper_subset(a: Iterable[A], b: Iterable[A]) -> bool:
    return subset(a, b) and not subset(b, a)


@dataclass(frozen=True)
class Argument:
    premises: List[Fact]
    conclusions: List[Fact]

    def __repr__(self, arrow: str='<-'):
        return '{0} {1} {2}'.format(
            ' ∧ '.join([str(fact) for fact
                        in sorted(self.conclusions, key=str)]),
            arrow,
            ' ∧ '.join([str(fact) for fact
                        in sorted(self.premises, key=str)]))

    @staticmethod
    def fromStr(s: str) -> 'Argument':
        s = s.replace(' ', '')
        if '->' in s:
            [premises, conclusions] = s.split('->')
        elif '<-' in s:
            [conclusions, premises] = s.split('<-')
        else:
            raise Exception("No arrow '<-' or '->' in string.")

        def _fromStr(s_: str) -> List[Fact]:
            return [Fact.fromStr(a) for a in split(',|∧', s_)]

        if premises == '':
            return Argument([], _fromStr(conclusions))
        else:
            return Argument(_fromStr(premises), _fromStr(conclusions))

    @property
    def case_made_by(self) -> List[Fact]:
        # An argument from 'P to not Q' makes the case 'P and not Q'
        # see Definition 2, page 132
        return self.premises + self.conclusions

    @property
    def positions(self) -> List[Fact]:
        return self.case_made_by

    @property
    def is_properly_presumptive(self) -> bool:
        return not subset(self.conclusions, self.premises)

    @property
    def is_a_presumption(self) -> bool:
        return self.premises == []

    def is_coherent_in(self, case_model: 'CaseModel') -> bool:
        return any([subset(self.positions, case.facts)
                    for case in case_model.cases])

    def is_conclusive_in(self, case_model: 'CaseModel') -> bool:
        return (self.is_coherent_in(case_model) and
                all([implies(subset(self.premises, case.facts),
                             subset(self.conclusions, case.facts))
                     for case in case_model.cases]))

    def is_presumptively_valid_in(self, case_model: 'CaseModel') -> bool:
        most_preferred_cases = case_model.most_preferred_cases(self.premises)
        return len(most_preferred_cases) > 0 and \
            all([subset(self.conclusions, case.facts)
                 for case in most_preferred_cases])

    def is_properly_defeasible_in(self, case_model: 'CaseModel') -> bool:
        return (self.is_presumptively_valid_in(case_model)
                and not self.is_conclusive_in(case_model))

    def is_defeated_by_in(self, circumstances: List[Fact], case_model: 'CaseModel') -> bool:
        return (self.is_presumptively_valid_in(case_model) and
                not Argument(self.premises + circumstances,
                             self.conclusions)
                    .is_presumptively_valid_in(case_model))

    def is_rebutted_by_in(self, circumstances: List[Fact], case_model: 'CaseModel') -> bool:
        def is_rebutted(fact: Fact) -> bool:
            return (Argument(self.premises + circumstances,
                             [fact.negation])
                    .is_presumptively_valid_in(case_model))
        return (self.is_defeated_by_in(circumstances, case_model) and
                any([is_rebutted(conclusion)
                     for conclusion in self.conclusions]))

    def is_undercut_by_in(self, circumstances: List[Fact], case_model: 'CaseModel') -> bool:
        return (self.is_defeated_by_in(circumstances, case_model) and
                not self.is_rebutted_by_in(circumstances, case_model))

    def is_excluded_by_in(self, circumstances: List[Fact], case_model: 'CaseModel') -> bool:
        return not (Argument(self.premises + circumstances,
                             self.conclusions)
                    .is_coherent_in(case_model))


@dataclass(frozen=True)
class Case:
    probability: float
    facts: List[Fact]
    
    def __repr__(self):
        return '{0}: {1}'.format(
            self.probability,
            ' ∧ '.join([str(fact) for fact
                        in sorted(self.facts, key=lambda x: x.statement)]))

    @staticmethod
    def fromStr(probability: Union[int, float], str: str) -> 'Case':
        facts = split(',|∧', str.replace(' ', ''))
        return Case(probability, [Fact.fromStr(fact) for fact in facts])

    def __hash__(self):
        return hash(frozenset(self.facts))

    def __eq__(self, other):
        return frozenset(self.facts) == frozenset(other.facts)

    def __add__(self, other: 'Case'):
        return Case(self.probability + other.probability,
                    self.facts + other.facts)

    def negate(self):
        negated_facts = [Fact(f.statement, not f.is_true)
                            for f in self.facts]
        return Case(facts=negated_facts, probability=self.probability)


def check_cases(cases_list, complete_case_list):
    for case1, case2 in cases_list:
        # Definition 1, page 131
        # ToDo: Implement condition 5
        assert case1.negate() not in complete_case_list, "Case Model not valid, condition 1 was violated"
        if not case1 == case2:
            assert not case1 + \
                case2 in complete_case_list, "Case Model not valid, condition 2 was violated"
        if case1 == case2:
            assert case1 == case2, "Case Model not valid, condition 3 was violated"
            # This is trivial
        if not (case1.probability >= case2.probability or case1.probability <= case2.probability):
            assert False, "Case Model not valid, condition 4 was violated"

@dataclass
class CaseModel:
    cases: List[Case]

    def __repr__(self):
        return '\n'.join([str(case) for case in self.cases])

    @staticmethod
    def fromStr(cases: List[Tuple[Union[int, float], str]]) -> 'CaseModel':
        return CaseModel([Case.fromStr(case[0], case[1])
                          for case in cases])

    @cached_property
    def valid(self, no_processes: int = 5):
        case_combinations = list(set(combinations(self.cases, 2)))
        case_combinations_splitted = [case_combinations[i::no_processes] for i in range(no_processes)]
        args = [(case_list, self.cases) for case_list in case_combinations_splitted]
        with Pool(5) as p:
            p.starmap(check_cases, args)
        return True

    def coherent(self, arg: Argument) -> Tuple[bool, Optional[Case]]:
        for case in self.cases:
            if subset(arg.premises, case.facts) and subset(arg.conclusions, case.facts) and case.probability > 0.0:
                return True, case
        return False, None

    def conclusive(self, arg: Argument) -> bool:
        return arg.is_conclusive_in(self)

    def presumptively_valid(self, arg: Argument) -> bool:
        coherent, coherent_case = self.coherent(arg)
        if coherent:
            for case in self.cases:
                if all([fact in case.facts for fact in arg.premises]):
                    if not coherent_case.probability >= case.probability:
                        return False
            return True
        return False

    def probability(self, fact: Fact) -> float:
        probability = 0.0
        for case in self.cases:
            if fact in case.facts:
                probability += case.probability
        return probability

    def conditional_probability(self, fact: Fact, given_fact: Fact) -> float:
        probability = 0.0
        for case in self.cases:
            if fact in case.facts and given_fact in case.facts:
                probability += case.probability
        return probability / self.probability(given_fact)

    def most_preferred_cases(self, facts: List[Fact]) -> List[Case]:
        most_preferred_cases = []
        max_priority = 0.0
        for case in self.cases:
            if subset(facts, case.facts):
                if case.probability > max_priority:
                    max_priority = case.probability
                    most_preferred_cases = [case]
                elif case.probability == max_priority:
                    most_preferred_cases.append(case)
        return most_preferred_cases
