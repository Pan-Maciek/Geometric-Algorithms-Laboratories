from definitions import *
from sortedcontainers.sortedset import SortedSet
from defs import *
from queue import PriorityQueue

intersections = set()
points = []

def get_neighbours(segment, state):
    index = state.index(segment)
    return (
        state[index - 1].segment if index > 0 else None, #above
        state[index + 1].segment if index < len(state) - 1 else None #bellow
    )

def get_intersection_point(segment1, segment2, starting_orientation):
    _, s1_end = segment1
    if get_orientation(s1_end, segment2) != starting_orientation: #check if lines intersect
        line1, line2 = segment1.line, segment2.line
        (s1x_min, _), (s1x_max, _) = segment1
        (s2x_min, _), (s2x_max, _) = segment2
        return intersection(line1, line2, (s1x_min, s1x_max), (s2x_min, s2x_max))
    return None


def add_intersection_if_exists(segment, neighbour, orientation, events):
    if neighbour and segment:
        point = get_intersection_point(segment, neighbour, orientation)
        if point:
            inter = (segment, neighbour)
            if inter not in intersections:
                intersections.add(inter)
                points.append(point)
                events.put((point, INTERSECT, [Key(segment), Key(neighbour)]))


def add_state_and_intersections(state, state_segment, events):
    state.add(state_segment)
    above, below = get_neighbours(state_segment, state)
    add_intersection_if_exists(state_segment.segment, above, BELOW, events)
    add_intersection_if_exists(state_segment.segment, below, ABOVE, events)

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
    state = SortedSet()
    points = []
    for start, end in data_set:
        points.append(start)
        points.append(end)
    all_points = PointsCollection(points, color='gray')
    all_lines = LinesCollection(data_set, color='gray')

    for point, event, segments in iter_events(events):
        if event == START:
            [skey] = segments
            add_state_and_intersections(state, skey, events)
            above, below = get_neighbours(skey, state)
            yield Scene([
                all_points,
                PointsCollection([ point ], color = 'red')
            ],[
                all_lines,
                LinesCollection(list(map(lambda x: x.segment, state))),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else []),
            ])
        elif event == END:
            [skey] = segments
            above, below = get_neighbours(skey, state)
            state.remove(skey)
            yield Scene([
                all_points,
                PointsCollection([ point ], color = 'red')
            ],[
                all_lines,
                LinesCollection(list(map(lambda x: x.segment, state))),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else []),
            ])
            add_intersection_if_exists(above, below, ABOVE, events)
        else:
            above, below = segments

            state.remove(above)
            state.remove(below)

            above.op = point
            below.op = point

            yield Scene([
                all_points,
                PointsCollection([ point ], color = 'red')
            ],[
                all_lines,
                LinesCollection(list(map(lambda x: x.segment, state))),
                LinesCollection([above.segment], color='red'),
                LinesCollection([below.segment], color='green')
            ])
            add_state_and_intersections(state, above, events)
            add_state_and_intersections(state, below, events)
