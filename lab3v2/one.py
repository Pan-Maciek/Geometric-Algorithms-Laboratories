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


def sweep(data_set):
    events = prepare_events(data_set)
    state = SortedSet() # (point, event, [skey])

    def get_neighbours(segment):
        index = state.index(segment)
        return (state[index - 1].segment if index > 0 else None, #above
            state[index + 1].segment if index < len(state) - 1 else None) #bellow


    def add_intersection_if_exists(segment, neighbour, orientation):
        if neighbour and segment:
            point = get_intersection_point(segment, neighbour, orientation)
            return True if point else False


    def add_intersections(state, skey):
        above, below = get_neighbours(skey)
        return add_intersection_if_exists(skey.segment, above, BELOW) or \
               add_intersection_if_exists(skey.segment, below, ABOVE)

    for _, event, segments in iter_events(events):
        if event == START:
            [skey] = segments
            state.add(skey)
            if add_intersections(state, skey):
                return True
        elif event == END:
            [skey] = segments
            above, below = get_neighbours(skey)
            state.remove(skey)
            if add_intersection_if_exists(above, below, ABOVE):
                return True
    return False