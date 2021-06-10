from logic import *
from typing import *
import itertools as it


def premise_candidates(columns: Dict[str, FrozenSet[str]]) -> List[List[Fact]]:
    premise_candidates = list(
        it.product(
            *[
                [*[[Fact(name, category)] for category in columns], []]
                for name, categories in columns.items()
            ]
        )
    )
    return [list(it.chain(*a)) for a in premise_candidates]


def fact_candidates(columns: Dict[str, FrozenSet[str]]) -> List[Fact]:
    return list(
        it.chain(
            *[
                [Fact(name, category, frozenset(categories)) for category in categories]
                for name, categories in columns.items()
            ]
        )
    )


def candidate_arguments(columns: Dict[str, FrozenSet[str]]) -> List[Argument]:
    return [
        Argument(ps, [c])
        for c, ps in it.product(fact_candidates(columns), premise_candidates(columns))
        if c not in ps and all([other not in ps for other in c.other_categories])
    ]


def namesAndCategories(case_model: CaseModel) -> Dict[str, FrozenSet[str]]:
    return dict(
        set(
            it.chain(
                *[
                    [(fact.statement, fact.categories) for fact in case.facts]
                    for case in case_model.cases
                ]
            )
        )
    )


def is_overly_specific(a: Argument, arguments: List[Argument]) -> bool:
    return any(
        [
            (
                proper_subset(argument.premises, a.premises)
                and set(argument.conclusions) == set(a.conclusions)
            )
            for argument in arguments
        ]
    )


def is_an_exception(a: Argument, arguments: List[Argument]) -> bool:
    # assumes that every argument only has 1 conclusion
    assert all([len(arg.conclusions) == 1 for arg in [a, *arguments]])
    return any(
        [
            (
                proper_subset(argument.premises, a.premises)
                and argument.conclusions[0].statement == a.conclusions[0].statement
                and argument.conclusions[0].category != a.conclusions[0].category
            )
            for argument in arguments
        ]
    )


def is_relevant(argument: Argument, others: List[Argument]) -> bool:
    return (not is_overly_specific(argument, others)) or is_an_exception(
        argument, others
    )


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
    return [
        Argument(list(premises), list(set(conclusions)))
        for premises, conclusions in grouped_by_premises.items()
    ]


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
) -> Set[FrozenSet[Fact]]:
    return {
        frozenset({fact, *premises})
        for fact in fact_candidates(namesAndCategories(case_model))
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


def is_applicable(known_facts: List[Fact], unknown_fact: str, arg: Argument):
    return subset(arg.premises, known_facts) and unknown_fact in [
        fact.statement for fact in arg.conclusions
    ]


def apply_argument(unknown_fact: str, arg: Argument) -> Fact:
    return next(fact for fact in arg.conclusions if fact.statement == unknown_fact)


def is_more_specific(a: Argument, b: Argument) -> bool:
    return subset(b.premises, a.premises)


def is_defeated(
    known_facts: List[Fact],
    unknown_fact: str,
    argument: Argument,
    other_arguments: List[Argument],
):
    prediction = apply_argument(unknown_fact, argument)
    any(
        [
            is_more_specific(other_argument, argument)
            and is_applicable(known_facts, unknown_fact, other_argument)
            and apply_argument(unknown_fact, other_argument) != prediction
            for other_argument in other_arguments
        ]
    )
