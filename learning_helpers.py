from logic import *
from typing import *
import itertools as it


def premise_candidates(names: List[str]) -> List[List[Fact]]:
    premise_candidates = list(
        it.product(*[[[Fact(name, True)], [Fact(name, False)], []] for name in names])
    )
    return [list(it.chain(*a)) for a in premise_candidates]


def fact_candidates(names: List[str]) -> List[Fact]:
    return list(it.chain(*[[Fact(name, True), Fact(name, False)] for name in names]))


def candidate_arguments(names: List[str]) -> List[Argument]:
    return [
        Argument(ps, [c])
        for c, ps in it.product(fact_candidates(names), premise_candidates(names))
        if c not in ps and c.negation not in ps
    ]


def filter_arguments(arguments: List[Argument]) -> List[Argument]:
    return [a for a in arguments if a.is_relevant(arguments)]


def join_arguments(arguments: List[Argument]) -> List[Argument]:
    grouped_by_premises: Dict[FrozenSet[Fact], List[Fact]] = dict()
    for argument in arguments:
        key = frozenset(argument.premises)
        if key in grouped_by_premises:
            grouped_by_premises[key] += argument.conclusions
        else:
            grouped_by_premises[key] = argument.conclusions
    return [
        Argument(list(premises), list(set(conclusions)))
        for premises, conclusions in grouped_by_premises.items()
    ]


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
        frozenset({fact, *premises})
        for fact in fact_candidates(case_model.names)
        if fact.statement != conclusion.statement
           and fact.statement not in {p.statement for p in premises}
    }


def more_specific_sets(subsets: Set[FrozenSet[Fact]]) -> Set[FrozenSet[Fact]]:
    """
    If a set contains a quality criterion (for example, conclusiveness), all its subsets must also fulfill it.
    Therefore, this function takes some sets of size n each
    -- like {{A, B, C, D}, {B, C, D, E}, {C, D, E, F}
    and returns all sets of size n+1 whose subsets are in the input set.
    -- like {{A, B, C, D, E}, {B, C, D, E, F}}
    These are all the sets of size n+1 that potentially fulfill the quality criterion.
    """
    return {
        a.union(b)
        for (a, b) in list(it.combinations(subsets, 2))
        if len(a.symmetric_difference(b)) == 2
    }
