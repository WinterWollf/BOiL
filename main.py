from activity import Activity, parseEventSequenceFormat, parsePredecessorformat
from cpm import CPM
from main_window import create_main_gui

def main():
    # Test data #

    # data = {
    #     'A': Activity('A', 2),
    #     'B': Activity('B', 5),
    #     'C': Activity('C', 1, ['A', 'B']),
    #     'D': Activity('D', 6, ['B']),
    #     'E': Activity('E', 4, ['C','D']),
    #     'F': Activity('F', 2, ['D']),
    # }

    # data = {
    #     'A': Activity('A', 3),
    #     'B': Activity('B', 4,['A']),
    #     'C': Activity('C', 6, ['A']),
    #     'D': Activity('D', 7, ['B']),
    #     'E': Activity('E', 1, ['D']),
    #     'F': Activity('F', 2, ['C']),
    #     'G': Activity('G', 3, ['C']),
    #     'H': Activity('H', 4, ['G']),
    #     'I': Activity('I', 1, ['E', 'F', 'H']),
    #     'J': Activity('J', 2, ['I']),
    # }

    # data = {
    #     'A': Activity('A', 3),
    #     'B': Activity('B', 4,['A']),
    #     'C': Activity('C', 6, ['A']),
    #     'D': Activity('D', 7, ['B']),
    #     'E': Activity('E', 1, ['D']),
    #     'F': Activity('F', 2, ['C']),
    #     'G': Activity('G', 3, ['C']),
    #     'H': Activity('H', 4, ['G']),
    #     'I': Activity('I', 1, ['E', 'F', 'H', 'K']),
    #     'J': Activity('J', 2, ['I']),
    #     'K': Activity('K', 5, ['B']),
    # }

    ###################

    # Zad 1 #

    data = {
        'A': {'duration': 2, 'events': '1-2'},
        'B': {'duration': 4, 'events': '2-3'},
        'C': {'duration': 3, 'events': '1-3'},
        'D': {'duration': 5, 'events': '3-4'},
        'E': {'duration': 2, 'events': '2-5'},
        'F': {'duration': 3, 'events': '4-6'},
        'G': {'duration': 4, 'events': '5-6'},
        'H': {'duration': 2, 'events': '6-7'},
    }

    data = parseEventSequenceFormat(data)

    # Zad 2 #

    # data = {
    #     'A': Activity('A', 3),
    #     'B': Activity('B', 5),
    #     'C': Activity('C', 2, ['A']),
    #     'D': Activity('D', 4, ['B']),
    #     'E': Activity('E', 3, ['B']),
    #     'F': Activity('F', 2, ['C', 'D']),
    #     'G': Activity('G', 4, ['E']),
    #     'H': Activity('H', 3, ['F', 'G']),
    #     'I': Activity('I', 2, ['H']),
    # }

    #results = CPM(data)
    #results.calculate()
    #results.print()
    #results.printCriticalPath()
    #results.drawAON()
    #results.drawAOA()
    #results.drawGantt()


if __name__ == "__main__":
    main()
    create_main_gui()