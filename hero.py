from typing import *
from queuelib.queue import FifoMemoryQueue
from itertools import *
from helpers import subset, histogram, unique
from fractions import Fraction

Fact = str
X = List[List[Fact]]
Y = List[Fact]
Premise = List[Fact]
Conclusion = Fact
Rule = Tuple[Premise, Conclusion]
Position = Fraction
Theory = List[Tuple[Rule, Position]]


def defeasible_theory_search(x: X, y: Y) -> Theory:
    premise_literals: List[Fact] = unique(list(chain(*x)))
    conclusion_literals = unique(y)
    theory: Theory = []
    while True:
        rule = rule_search(premise_literals, conclusion_literals, theory, x, y)
        if rule is None:
            break
        theory = [*theory, rule]
        # print(theory)
    return theory


def rule_search(
    premise_literals: List[Fact],
    conclusion_literals: List[Fact],
    theory: Theory,
    x: X,
    y: Y,
) -> Optional[Tuple[Rule, Fraction]]:
    best_gain = 0.0
    best_rule, position_of_best_rule = None, None
    for position in positions(theory):
        # print(position)
        weaker = [(r, p) for (r, p) in theory if p < position]
        stronger = [(r, p) for (r, p) in theory if p > position]
        queue = FifoMemoryQueue()  # Type: Queue of lists of facts
        queue.push([])
        while len(queue) > 0:
            premise = queue.pop()
            conclusion, gain_, max_gain_ = compute(
                premise, position, conclusion_literals, theory, x, y
            )
            if gain_ > best_gain:
                best_gain = gain_
                best_rule, position_of_best_rule = (premise, conclusion), position
            if max_gain_ > best_gain:
                for refinement in refinements(premise_literals, premise):
                    queue.push(refinement)
    if best_gain > 0:
        assert best_rule is not None
        assert position_of_best_rule is not None
        return best_rule, position_of_best_rule
    else:
        return None


def positions(theory: Theory) -> List[Position]:
    if len(theory) == 0:
        return [Fraction(0)]
    existing = sorted(position for rule, position in theory)
    positions = [Fraction(existing[0] - 1, 2)]
    for i in range(len(existing) - 1):
        positions.append(existing[i])
        positions.append(Fraction(existing[i] + existing[i + 1], 2))
    positions.append(existing[-1])
    positions.append(1 - Fraction(1 - existing[-1], 2))
    return positions


def compute(
    premise: Premise,
    position: Position,
    conclusion_literals: List[Fact],
    theory: Theory,
    x: X,
    y: Y,
) -> Tuple[Conclusion, float, float]:
    # print(
    #     [
    #         (
    #             c,
    #             gain((premise, c), position, theory, x, y),
    #             max_gain((premise, c), position, theory, x, y),
    #         )
    #         for c in conclusion_literals
    #     ],
    # )
    preferred_conclusion, gain_, _ = max(
        [
            (
                c,
                gain((premise, c), position, theory, x, y),
                max_gain((premise, c), position, theory, x, y),
            )
            for c in conclusion_literals
        ],
        key=lambda x: (x[1], x[2]),
    )
    max_gain_ = max(
        [max_gain((premise, c), position, theory, x, y) for c in conclusion_literals]
    )
    return preferred_conclusion, gain_, max_gain_


def gain(rule: Rule, position: Position, theory: Theory, x: X, y: Y):
    old_accuracy = accuracy(theory, x, y)
    new_accuracy = accuracy([*theory, (rule, position)], x, y)
    return new_accuracy - old_accuracy


def accuracy(theory: Theory, x: X, y: Y) -> float:
    data = list(zip(x, y))
    accurate = [1 for x, y in data if predict(x, theory) == y]
    return len(accurate) / len(data)


def max_gain(rule: Rule, position: Position, theory: Theory, x: X, y: Y):
    data = list(zip(x, y))
    hufflepuff = [
        1
        for x, y in data
        if predict(x, [*theory, (rule, position)]) == y and predict(x, theory) != y
    ]
    return len(hufflepuff) / len(data)


def predict(facts: List[Fact], theory: Theory) -> Optional[Conclusion]:
    applicable_rules = [
        ((premise, conclusion), position)
        for (premise, conclusion), position in theory
        if subset(premise, facts)
    ]
    if len(applicable_rules) == 0:
        return None
    strongest_applicable_position = max(applicable_rules, key=lambda x: x[1])[1]
    strongest_applicable_rules = [
        (rule, position)
        for rule, position in applicable_rules
        if position == strongest_applicable_position
    ]
    conclusions = {
        conclusion for (premise, conclusion), position in strongest_applicable_rules
    }
    if len(conclusions) == 1:
        return list(conclusions)[0]
    else:
        return None


def refinements(literals: List[Fact], premise: Premise) -> List[Premise]:
    return [[*premise, literal] for literal in literals if literal not in premise]


# main()
