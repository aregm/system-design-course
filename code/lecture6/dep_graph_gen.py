from __future__ import annotations

import json
import string
import random
import argparse


class ABaseIndex:
    _val: list[int]
    _base: int

    def __init__(self, base: int, value: int=0) -> None:
        assert base > 0
        self._base = base
        self._val = [0] if not value else []
        while value:
            self._val.append(value%base)
            value = value // base

    def __repr__(self) -> str:
        return self.__str__() 
    def __str__(self) -> str:
        return "ABaseIndex(" + str(self._base) +") = " + str(self._val)
    def __add__(self, other) -> ABaseIndex:
        return ABaseIndex(self._base, int(self) + int(other))
    def __sub__(self, other) -> ABaseIndex:
        return ABaseIndex(self._base, int(self) - int(other))
    def __int__(self) -> int:
        result = 0
        factor = 1
        for component in self._val:
            result += component * factor
            factor = factor * self._base
        return result
    def __lt__(self, other) -> bool:
        return int(self) < int(other)
    def __le__(self, other) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    def __eq__(self, other) -> bool:
        return int(self) == int(other)
    def __gt__(self, other) -> bool:
        return int(self) > int(other)
    def __ge__(self, other) -> bool:
        return self.__gt__(other) or self.__eq__(other)

    
    def internal_repr_as_index_list(self) -> list[int]:
        return reversed(self._val)


# lazy implementation that skips 'a's
def semilexi(n: int, alphabet=string.ascii_lowercase):
    assert len(alphabet)
    index = ABaseIndex(len(alphabet), 1)
    while index < n:
        yield "".join([alphabet[idx] for idx in index.internal_repr_as_index_list()])
        index = index + 1


def dag_gen(size: int, density: int, max_degree: int=10):
    assert size > 0
    assert 0 <= density <= 100
    assert max_degree >= 0
    names = [name for name in semilexi(size)]
    edges = {}

    for i in range(size-1):
        node_degree = random.randint(0, max_degree)
        edges[i] = []
        for j in range(i+1, size-1):
            if random.randint(0, 100) < density and node_degree:
                edges[i].append(j) 
                node_degree = node_degree - 1

    return names, edges 


def graph_to_json(names, edges, output):
    result = {}
    for idx, name in enumerate(names):
        result[name] = {"depends": [names[target] for target in edges[idx]], "rule": "build " + name}
    
    with open(output, 'w') as f:
        json.dump(result, f, indent=4, sort_keys=True)


parser = argparse.ArgumentParser(prog="Random build dependency DAG generator.")
parser.add_argument("filename", help="Output file name.")
parser.add_argument("-d", "--density", type=int, default=30, help="Specify graph density as a percentage of present edges (0-100).")
parser.add_argument("-s", "--size", type=int, default=10, help="Number of nodes in the generated graph.")
parser.add_argument("-m", "--max-degree", type=int, default=10, help="Generate no more than `max-degree` edges for a vertice.")

args = parser.parse_args()

nodes, edges = dag_gen(args.size, args.density, args.max_degree)
graph_to_json(nodes, edges, args.filename)
