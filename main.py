from activity import Activity
from cpm import CPM


def main():
    data = {
        'A': Activity('A', 2),
        'B': Activity('B', 5),
        'C': Activity('C', 1, ['A', 'B']),
        'D': Activity('D', 6, ['B']),
        'E': Activity('E', 4, ['C','D']),
        'F': Activity('F', 2, ['D']),
    }

    results = CPM(data)
    results.calculate()
    results.print()
    results.printCriticalPath()
    results.drawAON()


if __name__ == "__main__":
    main()
