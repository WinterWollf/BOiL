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
