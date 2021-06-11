from logic import *
from learning_helpers import *
from typing import *
import itertools as it
from operator import attrgetter


@dataclass
class Theory:
    conclusive_arguments: List[Argument]
    # presumptively valid arguments that are _not_ also conclusive:
    presumptively_valid_arguments: List[Argument]
    # coherent arguments that are _not_ also presumptively valid:
    coherent_arguments: List[Argument]

    def __repr__(
        self,
        conclusive_arguments=True,
        presumptively_valid_arguments=True,
        coherent_arguments=False,
    ) -> str:
        s = ""
        if conclusive_arguments:
            for a in sorted(self.conclusive_arguments, key=str):
                s += "\n" + str(a)
        if presumptively_valid_arguments:
            for a in sorted(self.presumptively_valid_arguments, key=str):
                s += "\n" + a.toStr(arrow="<~")
        if coherent_arguments:
            for a in sorted(self.coherent_arguments, key=str):
                s += a.toStr(arrow="<:")
        return s

    def __add__(self, other):
        return self.union([self, other])

    @property
    def size(self):
        return len(self.conclusive_arguments) + len(self.presumptively_valid_arguments)

    def predict(
        self, known_facts: List[Fact], unknown_fact: str
    ) -> Optional[Tuple[Fact, Argument]]:
        conclusive_args, presumptively_valid_args = [], []
        for argument in self.conclusive_arguments:
            if self.is_applicable(known_facts, unknown_fact, argument):
                conclusive_args.append(argument)
            if conclusive_args:
                selected_arg = max(conclusive_args, key=lambda item: len(item.premises))
                # return self.apply_argument(unknown_fact, argument), argument
                return self.apply_argument(unknown_fact, selected_arg), selected_arg
        for argument in self.presumptively_valid_arguments:

            other_arguments = [
                a
                for a in self.conclusive_arguments + self.presumptively_valid_arguments
                if a != argument
            ]
            if self.is_applicable(
                known_facts, unknown_fact, argument
            ) and not self.is_defeated(
                known_facts, unknown_fact, argument, other_arguments
            ):
                presumptively_valid_args.append(argument)
            if presumptively_valid_args:
                selected_arg = max(
                    presumptively_valid_args, key=lambda item: len(item.premises)
                )
                return self.apply_argument(unknown_fact, selected_arg), selected_arg
                # return self.apply_argument(unknown_fact, argument), argument
        return None

    @staticmethod
    def learn_with_naive_search(case_model: CaseModel) -> "Theory":
        theory = Theory([], [], [])
        for argument in candidate_arguments(case_model.namesAndCategories):
            if argument.is_conclusive_in(case_model):
                theory.conclusive_arguments.append(argument)
            elif argument.is_presumptively_valid_in(case_model):
                theory.presumptively_valid_arguments.append(argument)
            elif argument.is_coherent_in(case_model):
                theory.coherent_arguments.append(argument)
        return Theory(
            postprocess(theory.conclusive_arguments),
            postprocess(theory.presumptively_valid_arguments),
            postprocess(theory.coherent_arguments),
        )

    @staticmethod
    def union(*theories: "Theory") -> "Theory":
        def _union(argumentLists: List[List[Argument]]) -> List[Argument]:
            return list(it.chain(*argumentLists))

        return Theory(
            _union([theory.conclusive_arguments for theory in theories]),
            _union([theory.presumptively_valid_arguments for theory in theories]),
            _union([theory.coherent_arguments for theory in theories]),
        )

    @staticmethod
    def learn_with_pruned_search(
        case_model: CaseModel,
        depth: int = 5,
        max_premise_size: Optional[int] = None,
        log: bool = False,
    ) -> "Theory":
        theory = Theory.union(
            *[
                Theory.init_pruned_search(
                    candidate, case_model, depth, max_premise_size, log
                )
                for candidate in fact_candidates(case_model.namesAndCategories)
            ]
        )
        return Theory(
            join_arguments(theory.conclusive_arguments),
            join_arguments(theory.presumptively_valid_arguments),
            join_arguments(theory.coherent_arguments),
        )

    @staticmethod
    def init_pruned_search(
        conclusion: Fact,
        case_model: CaseModel,
        depth: int,
        max_premise_size: Optional[int],
        log: bool,
    ) -> "Theory":
        if log:
            print("learning", conclusion, "...")
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
                    [], conclusion, case_model, theory, depth, max_premise_size
                )
        return theory

    @staticmethod
    def pruned_search(
        premises: List[Fact],
        conclusion: Fact,
        case_model: CaseModel,
        theory: "Theory",
        depth: int,
        max_premise_size: Optional[int],
    ) -> "Theory":
        premise_size = 1
        premise_candidates = premise_candidates_(conclusion, premises, case_model)
        while len(premise_candidates) > 0 and (
            (premise_size <= max_premise_size) if max_premise_size is not None else True
        ):
            next_premise_candidates = set()
            for subset in premise_candidates:
                argument = Argument(list(subset), [conclusion])
                if argument.is_conclusive_in(case_model) and (
                    not argument.is_overly_specific(theory.conclusive_arguments)
                    or argument.is_an_exception(theory.presumptively_valid_arguments)
                ):
                    theory.conclusive_arguments.append(argument)
                else:
                    earlier_args = (
                        theory.conclusive_arguments
                        + theory.presumptively_valid_arguments
                    )
                    if (
                        argument.is_presumptively_valid_in(case_model)
                        and not argument.is_overly_specific(earlier_args)
                        and depth > 0
                    ):
                        theory.presumptively_valid_arguments.append(argument)
                        if depth > 1:
                            # Search for exceptions.
                            theory = Theory.union(
                                theory,
                                *[
                                    Theory.pruned_search(
                                        list(subset),
                                        category,
                                        case_model,
                                        Theory([], [], []),
                                        depth - 1,
                                        max_premise_size,
                                    )
                                    for category in conclusion.other_categories
                                ],
                            )
                    elif argument.is_coherent_in(case_model):
                        theory.coherent_arguments.append(argument)
                    if argument.is_coherent_in(case_model):
                        next_premise_candidates.add(subset)
            premise_size += 1
            premise_candidates = more_specific_sets(next_premise_candidates)
        return theory

    def is_defeated(
        self,
        known_facts: List[Fact],
        unknown_fact: str,
        argument: Argument,
        other_arguments: List[Argument],
    ):
        prediction = self.apply_argument(unknown_fact, argument)
        any(
            [
                self.is_more_specific(other_argument, argument)
                and self.is_applicable(known_facts, unknown_fact, other_argument)
                and self.apply_argument(unknown_fact, other_argument) != prediction
                for other_argument in other_arguments
            ]
        )

    @staticmethod
    def is_applicable(known_facts: List[Fact], unknown_fact: str, arg: Argument):
        return subset(arg.premises, known_facts) and unknown_fact in [
            fact.statement for fact in arg.conclusions
        ]

    @staticmethod
    def apply_argument(unknown_fact: str, arg: Argument) -> Fact:
        return next(fact for fact in arg.conclusions if fact.statement == unknown_fact)

    @staticmethod
    def is_more_specific(a: Argument, b: Argument) -> bool:
        return subset(b.premises, a.premises)
