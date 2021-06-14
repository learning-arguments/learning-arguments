from typing import *

A = TypeVar("A")
B = TypeVar("B")


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


def unique(
    l: List[A], f: Union[Callable[[A], B], Callable[[A], B]] = lambda x: x
) -> List[A]:
    # Inefficient but easy way to preserve the order.
    m = []
    n = []
    for a in l:
        if f(a) not in n:
            m.append(a)
            n.append(f(a))
    return m
