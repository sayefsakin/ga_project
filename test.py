from sortedcontainers import SortedList


if __name__ == "__main__":
    print('hello')
    a = SortedList()
    a.add((2, 345))
    a.add((10, 235))
    a.add((10, 22))
    a.add((8, 52))
    print(a)

