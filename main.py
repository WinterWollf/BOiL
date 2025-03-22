from activity import Activity
from cpm import CPM


def main():
    # data = {
    #     'A': Activity('A', 2),
    #     'B': Activity('B', 5),
    #     'C': Activity('C', 1, ['A', 'B']),
    #     'D': Activity('D', 6, ['B']),
    #     'E': Activity('E', 4, ['C','D']),
    #     'F': Activity('F', 2, ['D']),
    # }

    data = {
        'A': Activity('A', 3),
        'B': Activity('B', 4,['A']),
        'C': Activity('C', 6, ['A']),
        'D': Activity('D', 7, ['B']),
        'E': Activity('E', 1, ['D']),
        'F': Activity('F', 2, ['C']),
        'G': Activity('G', 3, ['C']),
        'H': Activity('H', 4, ['G']),
        'I': Activity('I', 1, ['E', 'F', 'H']),
        'J': Activity('J', 2, ['I']),
    }

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


    results = CPM(data)
    results.calculate()
    results.print()
    results.printCriticalPath()
    results.drawAON()


if __name__ == "__main__":
    main()
