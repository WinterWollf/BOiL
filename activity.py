class Activity:
    def __init__(self, name, duration, predecessors=None):
        self.name = name
        self.duration = duration
        self.predecessors = predecessors if predecessors else []
        self.ES = 0  # Early Start
        self.EF = 0  # Early Finish
        self.LS = 0  # Late Start
        self.LF = 0  # Late Finish
        self.reserve = 0