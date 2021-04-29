from typing import TypeVar, Union, Tuple, List, Set, Dict, FrozenSet, Callable
from dataclasses import dataclass
from operator import itemgetter
import itertools as it
import re


@dataclass(frozen=True)
class Fact:
    is_true: bool
    name: str

    def __str__(self) -> str:
        return ('' if self.is_true else '¬') + self.name

    @property
    def negation(self) -> 'Fact':
        return Fact(not self.is_true, self.name)

    @staticmethod
    def fromStr(str: str) -> 'Fact':
        if str[0] == '¬' or str[0] == '~':
            return Fact(False, str[1:])
        else:
            return Fact(True, str)


@dataclass
class Case:
    priority: float
    facts: FrozenSet[Fact]

    def __str__(self):
        return '{0}: {1}'.format(
            self.priority,
            ' ∧ '.join([str(fact) for fact
                        in sorted(self.facts, key=lambda x: x.name)]))

    @staticmethod
    def fromStr(priority: Union[int, float], str: str) -> 'Case':
        facts = re.split(',|∧', str.replace(' ', ''))
        return Case(priority, [Fact.fromStr(fact) for fact in facts])


@dataclass
class CaseModel:
    cases: List[Case]

    @staticmethod
    def fromStr(cases: List[Tuple[Union[int, float], str]]) -> 'CaseModel':
        return CaseModel([Case.fromStr(case[0], case[1])
                          for case in cases])

    def most_preferred_cases(self, facts: List[Fact]) -> List[Case]:
        most_preferred_cases = []
        max_priority = 0
        for case in self.cases:
            if subset(facts, case.facts):
                if case.priority > max_priority:
                    max_priority = case.priority
                    most_preferred_cases = [case]
                elif case.priority == max_priority:
                    most_preferred_cases.append(case)
        return most_preferred_cases


def implies(a: bool, b: bool) -> bool:
    return (not a) or b


def subset(a, b):
    return all([a_ in b for a_ in a])


def proper_subset(a, b):
    return subset(a, b) and not subset(b, a)


@dataclass(frozen=True)
class Argument:
    premises: List[Fact]
    conclusions: List[Fact]

    def __str__(self, arrow='<-'):
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
            return [Fact.fromStr(a) for a in re.split(',|∧', s_)]

        if premises == '':
            return Argument([], _fromStr(conclusions))
        else:
            return Argument(_fromStr(premises), _fromStr(conclusions))

    @property
    def case_made_by(self) -> List[Fact]:
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

    def is_coherent_in(self, case_model: CaseModel) -> bool:
        return any([subset(self.positions, case.facts)
                    for case in case_model.cases])

    def is_conclusive_in(self, case_model: CaseModel) -> bool:
        return (self.is_coherent_in(case_model) and
                all([implies(subset(self.premises, case.facts),
                             subset(self.conclusions, case.facts))
                     for case in case_model.cases]))

    def is_presumptively_valid_in(self, case_model: CaseModel) -> bool:
        most_preferred_cases = case_model.most_preferred_cases(self.premises)
        return len(most_preferred_cases) > 0 and \
            all([subset(self.conclusions, case.facts)
                 for case in most_preferred_cases])

    def is_properly_defeasible_in(self, case_model: CaseModel) -> bool:
        return (self.is_presumptively_valid_in(case_model)
                and not self.is_conclusive_in(case_model))

    def is_defeated_by_in(self, circumstances: List[Fact], case_model: CaseModel) -> bool:
        return (self.is_presumptively_valid_in(case_model) and
                not Argument(self.premises + circumstances,
                             self.conclusions)
                    .is_presumptively_valid_in(case_model))

    def is_rebutted_by_in(self, circumstances: List[Fact], case_model: CaseModel) -> bool:
        def is_rebutted(fact: Fact) -> bool:
            return (Argument(self.premises + circumstances,
                             [fact.negation])
                    .is_presumptively_valid_in(case_model))
        return (self.is_defeated_by_in(circumstances, case_model) and
                any([is_rebutted(conclusion)
                     for conclusion in self.conclusions]))

    def is_undercut_by_in(self, circumstances: List[Fact], case_model: CaseModel) -> bool:
        return (self.is_defeated_by_in(circumstances, case_model) and
                not self.is_rebutted_by_in(circumstances, case_model))

    def is_excluded_by_in(self, circumstances: List[Fact], case_model: CaseModel) -> bool:
        return not (Argument(self.premises + circumstances,
                             self.conclusions)
                    .is_coherent_in(case_model))


def premise_candidates(names: List[str]) -> List[List[Fact]]:
    premise_candidates = list(it.product(*[
        [[Fact(True, name)],
         [Fact(False, name)],
         []]
        for name in names]))
    return [list(it.chain(*a))
            for a in premise_candidates]


def fact_candidates(names: List[str]) -> List[Fact]:
    return list(it.chain(*[
        [Fact(True, name),
         Fact(False, name)]
        for name in names
    ]))


def candidate_arguments(names: List[str]) -> List[Argument]:
    return [Argument(ps, [c])
            for c, ps
            in it.product(
                fact_candidates(names),
                premise_candidates(names))
            if c not in ps and c.negation not in ps]


def names(case_model: CaseModel) -> List[str]:
    return list(set(it.chain(
        *[[fact.name for fact in case.facts]
          for case in case_model.cases])))


def is_overly_specific(a: Argument, arguments: List[Argument]) -> bool:
    return any([(proper_subset(argument.premises, a.premises) and
                set(argument.conclusions) == set(a.conclusions))
                for argument in arguments])


def is_an_exception(a: Argument, arguments: List[Argument]) -> bool:
    # assumes that every argument only has 1 conclusion
    assert all([len(arg.conclusions) == 1 for arg in [a, *arguments]])
    return any([(proper_subset(argument.premises, a.premises) and
                argument.conclusions[0].name == a.conclusions[0].name and
                argument.conclusions[0].is_true != a.conclusions[0].is_true)
                for argument in arguments])


def is_relevant(argument: Argument, others: List[Argument]) -> bool:
    return ((not is_overly_specific(argument, others))
            or is_an_exception(argument, others))


def filter_arguments(arguments: List[Argument]) -> List[Argument]:
    return [a for a in arguments if is_relevant(a, arguments)]


def join_arguments(arguments: List[Argument]) -> List[Argument]:
    grouped_by_premises: Dict[FrozenSet[Fact], List[Fact]] = dict()
    for argument in arguments:
        key = frozenset(argument.premises)
        if key in grouped_by_premises:
            grouped_by_premises[key] += argument.conclusions
        else:
            grouped_by_premises[key] = argument.conclusions
    return [Argument(list(premises), list(set(conclusions)))
            for premises, conclusions in grouped_by_premises.items()]


def postprocess(arguments: List[Argument]) -> List[Argument]:
    return join_arguments(filter_arguments(arguments))


def is_consistent(facts: List[Fact]) -> bool:
    true_names = {fact.name for fact in facts if fact.is_true}
    false_names = {fact.name for fact in facts if not fact.is_true}
    return len(true_names.intersection(false_names)) == 0


def premise_candidates_(
    conclusion: Fact, premises: List[Fact], case_model: CaseModel
) -> Set[FrozenSet[Fact]]:
    return {
        frozenset({fact, *premises}) for fact
        in fact_candidates(names(case_model))
        if fact.name != conclusion.name
        and fact.name not in {p.name for p in premises}}


def more_specific_sets(subsets: Set[FrozenSet[Fact]]) -> Set[FrozenSet[Fact]]:
    """
    If a set contains a quality criterion (for example, conclusiveness), all its subsets must also fulfill it. 
    Therefore, this function takes some sets of size n each
    -- like {{A, B, C, D}, {B, C, D, E}, {C, D, E, F}
    and returns all sets of size n+1 whose subsets are in the input set.
    -- like {{A, B, C, D, E}, {B, C, D, E, F}}
    These are all the sets of size n+1 that potentially fulfill the quality criterion.
    """
    return {a.union(b) for (a, b)
            in list(it.combinations(subsets, 2))
            if len(a.symmetric_difference(b)) == 2}


@dataclass
class Theory:
    conclusive_arguments: List[Argument]
    # presumptively valid arguments that are _not_ also conclusive:
    presumptively_valid_arguments: List[Argument]
    # coherent arguments that are _not_ also presumptively valid:
    coherent_arguments: List[Argument]

    def print(self,
              print_conclusive_arguments=True,
              print_presumptively_valid_arguments=True,
              print_coherent_arguments=False
              ) -> None:
        if print_conclusive_arguments:
            for a in sorted(self.conclusive_arguments, key=str):
                print(a)
        if print_presumptively_valid_arguments:
            for a in sorted(self.presumptively_valid_arguments, key=str):
                print(a.__str__(arrow='<~'))
        if print_coherent_arguments:
            for a in sorted(self.coherent_arguments, key=str):
                print(a.__str__(arrow='<:'))

    @staticmethod
    def learn_with_naive_search(case_model: CaseModel) -> 'Theory':
        theory = Theory([], [], [])
        for argument in candidate_arguments(names(case_model)):
            if argument.is_conclusive_in(case_model):
                theory.conclusive_arguments.append(argument)
            elif argument.is_presumptively_valid_in(case_model):
                theory.presumptively_valid_arguments.append(argument)
            elif argument.is_coherent_in(case_model):
                theory.coherent_arguments.append(argument)
        return Theory(
            postprocess(theory.conclusive_arguments),
            postprocess(theory.presumptively_valid_arguments),
            postprocess(theory.coherent_arguments)
        )

    @staticmethod
    def union(*theories: 'Theory') -> 'Theory':
        def _union(argumentLists: List[List[Argument]]) -> List[Argument]:
            return list(it.chain(*argumentLists))
        return Theory(
            _union([theory.conclusive_arguments for theory in theories]),
            _union([theory.presumptively_valid_arguments for theory in theories]),
            _union([theory.coherent_arguments for theory in theories])
        )

    @staticmethod
    def learn_with_pruned_search(case_model: CaseModel, depth: int = 5, log : bool = False) -> 'Theory':
        theory = Theory.union(
            *[Theory.init_pruned_search(
                candidate, case_model, depth, log)
              for candidate in fact_candidates(names(case_model))])
        return Theory(
            join_arguments(theory.conclusive_arguments),
            join_arguments(theory.presumptively_valid_arguments), join_arguments(
                theory.coherent_arguments)
        )

    @staticmethod
    def init_pruned_search(
            conclusion: Fact, case_model: CaseModel, depth: int, log: bool
    ) -> 'Theory':
        if log:
            print('learning', conclusion, '...')
        theory = Theory([], [], [])
        argument = Argument([], [conclusion])
        if argument.is_conclusive_in(case_model):
            theory.conclusive_arguments.append(argument)
        else:
            if argument.is_presumptively_valid_in(case_model) and depth > 0:
                theory.presumptively_valid_arguments.append(argument)
                # Searching for exceptions to this is already taken care of
                # by calling `init_pruned_search` on the negated conclusion.
            elif argument.is_coherent_in(case_model):
                theory.coherent_arguments.append(argument)
            if argument.is_coherent_in(case_model):
                theory = Theory.pruned_search(
                    [], conclusion, case_model, theory, depth)
        return theory

    @staticmethod
    def pruned_search(
            premises: List[Fact], conclusion: Fact,
            case_model: CaseModel, theory: 'Theory',
            depth: int
    ) -> 'Theory':
        premise_candidates = premise_candidates_(
            conclusion, premises, case_model)
        while len(premise_candidates) > 0:
            next_premise_candidates = set()
            for subset in premise_candidates:
                argument = Argument(list(subset), [conclusion])
                if argument.is_conclusive_in(case_model) and \
                    (not is_overly_specific(argument, theory.conclusive_arguments)
                     or is_an_exception(argument, theory.presumptively_valid_arguments)):
                    theory.conclusive_arguments.append(argument)
                else:
                    earlier_args = theory.conclusive_arguments + \
                        theory.presumptively_valid_arguments
                    if argument.is_presumptively_valid_in(case_model) \
                            and not is_overly_specific(argument, earlier_args) \
                            and depth > 0:
                        theory.presumptively_valid_arguments.append(argument)
                        if depth > 1:
                            # Search for exceptions.
                            theory = Theory.union(
                                theory,
                                Theory.pruned_search(
                                    list(subset), conclusion.negation,
                                    case_model, Theory([], [], []), depth - 1))
                    elif argument.is_coherent_in(case_model):
                        theory.coherent_arguments.append(argument)
                    if argument.is_coherent_in(case_model):
                        next_premise_candidates.add(subset)
            premise_candidates = more_specific_sets(next_premise_candidates)
        return theory
