from typing import *
from dataclasses import dataclass
from itertools import combinations
from multiprocessing import Pool
from re import split
from functools import cached_property
from helpers import subset, proper_subset, implies
import itertools as it


@dataclass(frozen=True)
class Fact:
    statement: str
    category: str = "true"
    categories: FrozenSet[str] = frozenset(["true", "false"])

    def __repr__(self) -> str:
        return (
            ""
            if self.category == "true"
            else ("¬" if self.category == "false" else self.category + "_")
        ) + self.statement

    @property
    def other_categories(self) -> List["Fact"]:
        return [
            Fact(self.statement, category, self.categories)
            for category in self.categories
        ]

    @staticmethod
    def fromStr(str: str, categories: List[str] = ["true", "false"]) -> "Fact":
        if "_" in str:
            prefix, rest = str.split("_", maxsplit=1)
            assert prefix in categories
            return Fact(rest, prefix, frozenset(categories))
        else:
            if str[0] == "¬" or str[0] == "~":
                return Fact(str[1:], "false")
            else:
                return Fact(str, "true")



@dataclass(frozen=True)
class Argument:
    premises: List[Fact]
    conclusions: List[Fact]

    def toStr(self, arrow: str = "<-") -> str:
        return "{0} {1} {2}".format(
            " ∧ ".join([str(fact) for fact in sorted(self.conclusions, key=str)]),
            arrow,
            " ∧ ".join([str(fact) for fact in sorted(self.premises, key=str)]),
        )

    def __repr__(self) -> str:
        return self.toStr()

    @staticmethod
    def fromStr(s: str) -> "Argument":
        s = s.replace(" ", "")
        if "->" in s:
            [premises, conclusions] = s.split("->")
        elif "<-" in s:
            [conclusions, premises] = s.split("<-")
        else:
            raise Exception("No arrow '<-' or '->' in string.")

        def _fromStr(s_: str) -> List[Fact]:
            return [Fact.fromStr(a) for a in split(",|∧", s_)]

        if premises == "":
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

    def is_coherent_in(self, case_model: "CaseModel") -> bool:
        return any([subset(self.positions, case.facts) for case in case_model.cases])

    def is_conclusive_in(self, case_model: "CaseModel") -> bool:
        return self.is_coherent_in(case_model) and all(
            [
                implies(
                    subset(self.premises, case.facts),
                    subset(self.conclusions, case.facts),
                )
                for case in case_model.cases
            ]
        )

    def is_presumptively_valid_in(self, case_model: "CaseModel") -> bool:
        most_preferred_cases = case_model.most_preferred_cases(self.premises)
        return len(most_preferred_cases) > 0 and all(
            [subset(self.conclusions, case.facts) for case in most_preferred_cases]
        )

    def is_properly_defeasible_in(self, case_model: "CaseModel") -> bool:
        return self.is_presumptively_valid_in(case_model) and not self.is_conclusive_in(
            case_model
        )

    def is_defeated_by_in(
            self, circumstances: List[Fact], case_model: "CaseModel"
    ) -> bool:
        return self.is_presumptively_valid_in(case_model) and not Argument(
            self.premises + circumstances, self.conclusions
        ).is_presumptively_valid_in(case_model)

    def is_rebutted_by_in(
            self, circumstances: List[Fact], case_model: "CaseModel"
    ) -> bool:
        def is_rebutted(fact: Fact) -> bool:
            return any(
                [
                    Argument(
                        self.premises + circumstances, [category]
                    ).is_presumptively_valid_in(case_model)
                    for category in fact.other_categories
                ]
            )

        return self.is_defeated_by_in(circumstances, case_model) and any(
            [is_rebutted(conclusion) for conclusion in self.conclusions]
        )

    def is_undercut_by_in(
            self, circumstances: List[Fact], case_model: "CaseModel"
    ) -> bool:
        return self.is_defeated_by_in(
            circumstances, case_model
        ) and not self.is_rebutted_by_in(circumstances, case_model)

    def is_excluded_by_in(
            self, circumstances: List[Fact], case_model: "CaseModel"
    ) -> bool:
        return not (
            Argument(self.premises + circumstances, self.conclusions).is_coherent_in(
                case_model
            )
        )

    def is_overly_specific(self, arguments: List['Argument']) -> bool:
        return any(
            [(proper_subset(argument.premises, self.premises) and set(argument.conclusions) == set(self.conclusions))
             for argument in arguments])

    def is_relevant(self, others: List['Argument']) -> bool:
        return (not self.is_overly_specific(others)) or self.is_an_exception(others)

    def is_an_exception(self, arguments: List['Argument']) -> bool:
        # assumes that every argument only has 1 conclusion
        assert all([len(arg.conclusions) == 1 for arg in [self, *arguments]])
        return any(
            [
                (
                        proper_subset(argument.premises, self.premises)
                        and argument.conclusions[0].statement == self.conclusions[0].statement
                        and argument.conclusions[0].is_true != self.conclusions[0].is_true
                )
                for argument in arguments
            ]
        )


@dataclass(frozen=True)
class Case:
    probability: float
    facts: List[Fact]

    def __repr__(self):
        return "{0}: {1}".format(
            self.probability,
            " ∧ ".join(
                [str(fact) for fact in sorted(self.facts, key=lambda x: x.statement)]
            ),
        )

    @staticmethod
    def fromStr(probability: Union[int, float], str: str) -> "Case":
        facts = split(",|∧", str.replace(" ", ""))
        return Case(probability, [Fact.fromStr(fact) for fact in facts])

    def __hash__(self):
        return hash(frozenset(self.facts))

    def __eq__(self, other):
        return frozenset(self.facts) == frozenset(other.facts)

    def __add__(self, other: "Case"):
        return Case(self.probability + other.probability, self.facts + other.facts)


def check_cases(cases_list, complete_case_list):
    for case1, case2 in cases_list:
        # Definition 1, page 131
        # ToDo: Implement condition 5
        assert all(
            [
                frozenset([fact])
                not in [frozenset(case.facts) for case in complete_case_list]
                for fact in case1.facts
            ]
        ), "Case Model not valid, condition 1 was violated"
        if not case1 == case2:
            assert (
                not case1 + case2 in complete_case_list
            ), "Case Model not valid, condition 2 was violated"
        if case1 == case2:
            assert case1 == case2, "Case Model not valid, condition 3 was violated"
            # This is trivial
        if not (
                case1.probability >= case2.probability
                or case1.probability <= case2.probability
        ):
            assert False, "Case Model not valid, condition 4 was violated"


@dataclass
class CaseModel:
    cases: List[Case]

    def __repr__(self):
        return "\n".join([str(case) for case in self.cases])

    @staticmethod
    def fromStr(cases: List[Tuple[Union[int, float], str]]) -> "CaseModel":
        return CaseModel([Case.fromStr(case[0], case[1]) for case in cases])

    @cached_property
    def valid(self, no_processes: int = 5):
        case_combinations = list(set(combinations(self.cases, 2)))
        case_combinations_splitted = [
            case_combinations[i::no_processes] for i in range(no_processes)
        ]
        args = [(case_list, self.cases) for case_list in case_combinations_splitted]
        with Pool(5) as p:
            p.starmap(check_cases, args)
        return True

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
        max_probability = 0.0
        for case in self.cases:
            if subset(facts, case.facts):
                if case.probability > max_probability:
                    max_probability = case.probability
                    most_preferred_cases = [case]
                elif case.probability == max_probability:
                    most_preferred_cases.append(case)
        return most_preferred_cases

    @property
    def names(self) -> List[str]:
        return list(set(it.chain(*[[fact.statement for fact in case.facts] for case in self.cases])))
