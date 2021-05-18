from logic import *
from typing import *
import itertools as it

def premise_candidates(names: List[str]) -> List[List[Fact]]:
    premise_candidates = list(it.product(*[
        [[Fact(name, True)],
         [Fact(name, False)],
         []]
        for name in names]))
    return [list(it.chain(*a))
            for a in premise_candidates]


def fact_candidates(names: List[str]) -> List[Fact]:
    return list(it.chain(*[
        [Fact(name, True),
         Fact(name, False)]
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
        *[[fact.statement for fact in case.facts]
          for case in case_model.cases])))


def is_overly_specific(a: Argument, arguments: List[Argument]) -> bool:
    return any([(proper_subset(argument.premises, a.premises) and
                set(argument.conclusions) == set(a.conclusions))
                for argument in arguments])


def is_an_exception(a: Argument, arguments: List[Argument]) -> bool:
    # assumes that every argument only has 1 conclusion
    assert all([len(arg.conclusions) == 1 for arg in [a, *arguments]])
    return any([(proper_subset(argument.premises, a.premises) and
                argument.conclusions[0].statement == a.conclusions[0].statement and
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
    true_names = {fact.statement for fact in facts if fact.is_true}
    false_names = {fact.statement for fact in facts if not fact.is_true}
    return len(true_names.intersection(false_names)) == 0


def premise_candidates_(
    conclusion: Fact, premises: List[Fact], case_model: CaseModel
) -> Set[FrozenSet[Fact]]:
    return {
        frozenset({fact, *premises}) for fact
        in fact_candidates(names(case_model))
        if fact.statement != conclusion.statement
        and fact.statement not in {p.statement for p in premises}}


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

    def __repr__(self,
                 conclusive_arguments=True,
                 presumptively_valid_arguments=True,
                 coherent_arguments=False
                 ) -> str:
        s = ''
        if conclusive_arguments:
            for a in sorted(self.conclusive_arguments, key=str):
                s += '\n' + str(a)
        if presumptively_valid_arguments:
            for a in sorted(self.presumptively_valid_arguments, key=str):
                s += '\n' + a.__repr__(arrow='<~')
        if coherent_arguments:
            for a in sorted(self.coherent_arguments, key=str):
                s += a.__repr__(arrow='<:')
        return s

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
    def learn_with_pruned_search(case_model: CaseModel, depth: int = 5, log: bool = False) -> 'Theory':
        theory = Theory.union(
            *[Theory.init_pruned_search(
                candidate, case_model, depth, log)
              for candidate in fact_candidates(names(case_model))])
        return Theory(
            join_arguments(theory.conclusive_arguments),
            join_arguments(theory.presumptively_valid_arguments), 
            join_arguments(theory.coherent_arguments)
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
