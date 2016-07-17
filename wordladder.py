from collections import defaultdict, deque
from itertools import combinations, imap
from operator import ne as notequals
from timeit import timeit
from unittest import TestCase
import sys


fixtures = [
    {
        "start": "hit",
        "end": "cog",
        "dictionary": [
            "hot", "dot", "dog", "lot", "log"
        ],
    },
    {
        "start": "hit",
        "end": "cog",
        "dictionary": [
            "hat", "hot", "dot", "dog", "lot", "log", "fog", "col",
            "hut", "mut", "mug", "dug", "lug", "cug", "dig", "dag",
        ],
    },
    {
        "start": "aaa",
        "end": "zzz",
        "dictionary": [
            "aab", "aba", "abb", "bbb", "bbc", "bcc", "ccc", "ccd",
            "cce", "cee", "zcz", "zze", "zzb", "zzc", "zzz", "ccz",
        ],
    }
]


class GraphBase(object):
    """This class provides the basic functionalities
    to deal with the internal graph representation, utilized by
    the solutions' concrete objects.
    """

    def is_next_to(self, w1, w2):
        """Check whether the hamming distance is 1"""
        return sum(imap(notequals, w1, w2)) == 1

    def add_edge(self, w1, w2):
        """Add a new arc and update the respective adjacency list"""
        self.next_of[w1].add(w2), self.next_of[w2].add(w1)

    def __init__(self, dictionary, start, end):
        self.dictionary = dictionary
        self.start = start
        self.end = end
        self.next_of = defaultdict(lambda: set())
        self.build()


class BfsSearchMixin(object):

    def search(self):
        # Aliases
        next_of, start, end = self.next_of, self.start, self.end
        fifo = deque([(start, [start])])
        while fifo:
            (cur, visited) = fifo.popleft()
            for next in next_of[cur] - set(visited):
                if next == end:
                    return len(visited)
                else:
                    fifo.append((next, visited + [next]))

        raise Exception("There is no possible transformation sequence "
                        "between {start} and {end}".format(
                            start=self.start, end=self.end))


class DijkstraSearchMixin(object):

    def search(self):
        # Aliases
        next_of, start, end = self.next_of, self.start, self.end
        dictionary = set(self.dictionary + [start, end])
        distance = defaultdict(lambda: float("inf"))
        distance[start] = 0
        while dictionary:
            word = min(dictionary, key=lambda x: distance[x])
            dictionary.remove(word)
            if distance[word] == float("inf"):
                break
            for next in next_of[word]:
                new_dist = 1 + distance[word]
                if new_dist < distance[next]:
                    distance[next] = new_dist

        return distance[end]


class AllEdgesBuildMixin(GraphBase):
    """
    Assumptions on words given as dictionary:

     - There are no dups.
     - They're all the same length
    """

    def build(self):
        dictionary = deque(self.dictionary + [self.start, self.end])
        while dictionary:
            word = dictionary.popleft()
            for candidate in dictionary:
                if self.is_next_to(word, candidate):
                    self.add_edge(word, candidate)


class BucketsBuildMixin(GraphBase):

    def build(self):
        dictionary = self.dictionary + [self.start, self.end]
        d = {}
        for word in dictionary:
            for i in range(len(word)):
                bucket = word[:i] + '_' + word[i+1:]
                if bucket in d:
                    d[bucket].append(word)
                else:
                    d[bucket] = [word]
        for words in d.values():
            for w1, w2 in combinations(words, 2):
                self.add_edge(w1, w2)


class TestCaseMixin(object):

    def test_swap_start_end(self):
        for fixture in self.fixtures:
            alt_start = fixture["end"]
            alt_end = fixture["start"]
            self.assertEqual(
                self.solution_cls(**fixture).search(),
                self.solution_cls(dictionary=fixture["dictionary"],
                                  start=alt_end, end=alt_start).search()
            )


class BuildAllEdgesSearchWithBfs(AllEdgesBuildMixin, BfsSearchMixin):
    pass


class BuildAllEdgesSearchWithDijkstra(AllEdgesBuildMixin, DijkstraSearchMixin):
    pass


class BuildBucketsSearchWithBfs(BucketsBuildMixin, BfsSearchMixin):
    pass


class BuildBucketsSearchWithDijkstra(BucketsBuildMixin, DijkstraSearchMixin):
    pass


class TestBuildAllEdgesSearchWithBfs(TestCase, TestCaseMixin):
    solution_cls = BuildAllEdgesSearchWithBfs
    fixtures = fixtures


class TestBuildAllEdgesSearchWithDijkstra(TestCase, TestCaseMixin):
    solution_cls = BuildAllEdgesSearchWithDijkstra
    fixtures = fixtures


class TestBuildBucketsSearchWithBfs(TestCase, TestCaseMixin):
    solution_cls = BuildBucketsSearchWithBfs
    fixtures = fixtures


class TestBuildBucketsSearchWithDijkstra(TestCase, TestCaseMixin):
    solution_cls = BuildBucketsSearchWithDijkstra
    fixtures = fixtures


if __name__ == "__main__":
    try:
        from prettytable import PrettyTable
    except ImportError:
        sys.exit("This module needs prettytable!")

    solutions = (BuildAllEdgesSearchWithBfs,
                 BuildAllEdgesSearchWithDijkstra,
                 BuildBucketsSearchWithBfs,
                 BuildBucketsSearchWithDijkstra)
    table = PrettyTable(["Fixture"] + [
        solution.__name__ for solution in solutions])

    for i, fixture in enumerate(fixtures):
        ret_and_time = []
        for solution in solutions:
            cls_name = solution.__name__
            ret = solution(**fixture).search()
            ret_and_time.append(
                (ret, timeit(
                    """{cls_name}(**fixture).search()""".format(
                        cls_name=cls_name),
                    setup="""from __main__ import {cls_name}, fixture""".format(
                        cls_name=cls_name),
                    number=10000,
                ))
            )

        table.add_row([i] + ret_and_time)

    print table
