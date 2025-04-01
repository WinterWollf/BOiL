from collections import deque

class Activity:
    def __init__(self, name, duration, predecessors=None):
        self.name = name
        self.duration = duration
        self.predecessors = predecessors if predecessors else []
        self.ES = 0
        self.EF = 0
        self.LS = 0
        self.LF = 0
        self.reserve = 0


def parsePredecessorformat(predecessor_data):
    """
    Input: Dictionary with activity names, durations, and predecessors.
    Output: Dictionary of Activity objects.
    """
    activities = {}
    for name, info in predecessor_data.items():
        activities[name] = Activity(name, info['duration'], info.get('predecessors', []))
    return activities


def parseEventSequenceFormat(event_data):
    """
    Input: Dictionary with activity names, durations, and event sequences (e.g., '1-2').
    Output: Dictionary of Activity objects with computed predecessors.
    """

    event_starts = {}
    event_ends = {}
    activities_temp = {}

    for name, info in event_data.items():
        duration = info['duration']
        start_event, end_event = map(int, info['events'].split('-'))

        activities_temp[name] = {'duration': duration, 'start': start_event, 'end': end_event}

        if start_event not in event_starts:
            event_starts[start_event] = []
        if end_event not in event_ends:
            event_ends[end_event] = []
        event_starts[start_event].append(name)
        event_ends[end_event].append(name)

    activities = {}
    for name, info in activities_temp.items():
        start_event = info['start']
        predecessors = event_ends.get(start_event, [])
        activities[name] = Activity(name, info['duration'], predecessors)

    return activities

def reverseEventSequenceFormat(activities):
    """
    Input: Dictionary of Activity objects (with attributes: name, duration, predecessors)
    Output: Dictionary in the event_data format
    """
    
    successors = {name: [] for name in activities}
    for name, activity in activities.items():
        for pred in activity.predecessors:
            if pred not in successors:
                raise ValueError(f"Predecessor {pred} for activity {name} is not in activities")
            successors[pred].append(name)
    
    
    in_degree = {name: len(activity.predecessors) for name, activity in activities.items()}
    queue = deque([name for name, degree in in_degree.items() if degree == 0])
    topo_order = []
    
    while queue:
        curr = queue.popleft()
        topo_order.append(curr)
        for succ in successors[curr]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)
    
    if len(topo_order) != len(activities):
        raise ValueError("Cycle detected or some activities are unreachable, invalid dependency graph.")
    
    
    start_events = {}
    end_events = {}
    next_event = 2
    
    for name in topo_order:
        activity = activities[name]
        
        if not activity.predecessors:
            start_events[name] = 1
        else:
            common = None
            for pred in activity.predecessors:
                if pred not in end_events:
                    raise ValueError(f"Predecessor {pred} for activity {name} has no assigned end event yet.")
                if common is None:
                    common = end_events[pred]
                elif end_events[pred] != common:
                    raise ValueError(f"Inconsistent end events among predecessors of activity {name}.")
            start_events[name] = common
        
        
        end_events[name] = next_event
        next_event += 1

    
    event_data = {}
    for name, activity in activities.items():
        event_data[name] = {
            'duration': activity.duration,
            'events': f"{start_events[name]}-{end_events[name]}"
        }
    
    return event_data
