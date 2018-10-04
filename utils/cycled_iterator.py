class CycledIterator:
    def __init__(self, arr):
        self.arr = arr
        self.current = -1 # we will increase current in __next__

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1

        if self.current + 1 > len(self.arr):
            self.current = 0

        return self.arr[self.current]

    def get_batch(self, n):
        return [next(self) for i in range(n)]
