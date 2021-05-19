from typing import *

A = TypeVar("A")


def implies(a: bool, b: bool) -> bool:
    return (not a) or b


def subset(a: Iterable[A], b: Iterable[A]) -> bool:
    return all([a_ in b for a_ in a])


def proper_subset(a: Iterable[A], b: Iterable[A]) -> bool:
    return subset(a, b) and not subset(b, a)


def histogram(l: List[A]) -> Dict[A, int]:
    histogram: Dict[A, int] = dict()
    for a in l:
        if a in histogram.keys():
            histogram[a] = histogram[a] + 1
        else:
            histogram[a] = 1
    return histogram
