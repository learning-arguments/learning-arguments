from logic import *
from typing import *
import itertools as it
from helpers import *


def premise_candidates(columns: Dict[str, List[str]]) -> List[List[Fact]]:
    premise_candidates = list(
        it.product(
            *[
                [*[[Fact(name, category)] for category in columns], []]
                for name, categories in columns.items()
            ]
        )
    )
    return [list(it.chain(*a)) for a in premise_candidates]


def fact_candidates(columns: Dict[str, List[str]]) -> List[Fact]:
    return list(
        it.chain(
            *[
                [Fact(name, category, categories) for category in categories]
                for name, categories in columns.items()
            ]
        )
    )


def candidate_arguments(columns: Dict[str, List[str]]) -> List[Argument]:
    return [
        Argument(ps, [c])
        for c, ps in it.product(fact_candidates(columns), premise_candidates(columns))
        if c not in ps and all([other not in ps for other in c.other_categories])
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
    return sorted(
        [
            Argument(list(premises), list(set(conclusions)))
            for premises, conclusions in grouped_by_premises.items()
        ],
        key=str,
    )


def postprocess(arguments: List[Argument]) -> List[Argument]:
    return join_arguments(filter_arguments(arguments))


def is_consistent(facts: List[Fact]) -> bool:
    return all(
        [
            [
                implies(
                    fact1.statement == fact2.statement, fact1.category != fact2.category
                )
                for fact1 in facts
            ]
            for fact2 in facts
        ]
    )


def premise_candidates_(
    conclusion: Fact, premises: List[Fact], case_model: CaseModel
) -> List[List[Fact]]:
    return [
        unique([fact, *premises])
        for fact in fact_candidates(case_model.namesAndCategories)
        if fact.statement != conclusion.statement
        and fact.statement not in {p.statement for p in premises}
    ]


def more_specific_sets(subsets: List[List[Fact]]) -> List[List[Fact]]:
    """
    If a set contains a quality criterion (for example, conclusiveness), all its subsets must also fulfill it.
    Therefore, this function takes some sets of size n each
    -- like {{A, B, C, D}, {B, C, D, E}, {C, D, E, F}
    and returns all sets of size n+1 whose subsets are in the input set.
    -- like {{A, B, C, D, E}, {B, C, D, E, F}}
    These are all the sets of size n+1 that potentially fulfill the quality criterion.
    """
    return [
        unique(a+b)
        for (a, b) in list(it.combinations(subsets, 2))
        if len(symmetric_difference(a, b)) == 2
    ]
