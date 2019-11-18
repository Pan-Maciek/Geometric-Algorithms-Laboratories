from sortedcontainers.sortedset import SortedSet
from defs import *
from queue import PriorityQueue
from definitions import *


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


def algo_visual(data_set):
    events = prepare_events(data_set)
    state = SortedSet() # (point, event, [skey])
    intersections = []
    points = []
    all_points = []
    for start, end in data_set:
        all_points.append(start)
        all_points.append(end)
    all_points = PointsCollection(all_points, color='gray')
    all_lines = LinesCollection(data_set, color='gray')
    yield Scene([ all_points ],[ all_lines ])

    def get_neighbours(segment):
        index = state.index(segment)
        return (state[index - 1].segment if index > 0 else None, #above
            state[index + 1].segment if index < len(state) - 1 else None) #bellow


    def swap_on(point, segments):
        above, below = segments
        state.remove(above)
        state.remove(below)

        above.op = below.op = point

        state.add(above)
        state.add(below)

    def add_intersection_if_exists(segment, neighbour, orientation):
        if neighbour and segment:
            point = get_intersection_point(segment, neighbour, orientation)
            if point:
                inter = tuple(sorted([segment, neighbour]))
                if inter not in intersections:
                    intersections.append(inter)
                    points.append(point)
                    events.put((point, INTERSECT, [Key(segment), Key(neighbour)]))


    def add_intersections(state, skey):
        above, below = get_neighbours(skey)
        add_intersection_if_exists(skey.segment, above, BELOW)
        add_intersection_if_exists(skey.segment, below, ABOVE)

    for point, event, segments in iter_events(events):
        if event == START:
            [skey] = segments
            state.add(skey)
            add_intersections(state, skey)
            above, below = get_neighbours(skey)
            yield Scene([ 
                all_points,
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else []),
            ])
        elif event == END:
            [skey] = segments
            above, below = get_neighbours(skey)
            state.remove(skey)
            add_intersection_if_exists(above, below, ABOVE)
            yield Scene([ 
                all_points,
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else []),
            ])
        else:
            above, below = segments
            swap_on(point, segments)

            add_intersections(state, above)
            add_intersections(state, below)
            yield Scene([ 
                all_points,
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                LinesCollection([below.segment], color='red'),
                LinesCollection([above.segment], color='green')
            ])

