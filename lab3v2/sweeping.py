from sortedcontainers.sortedset import SortedSet
from defs import *
from queue import PriorityQueue


def prepare_events(data_set):
    pq = PriorityQueue()
    for segment in data_set:
        start, end = segment
        pq.put((start, START, [Key(segment)]))
        pq.put((end, END, [Key(segment)]))
    return pq

def iter_events(events):
    while not (events.empty()):
        yield events.get()
