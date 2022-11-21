'''
Created on 2 окт. 2022 г.

@author: PaiNt
'''


class _StackQueue:

    def __new__(cls, *args, **kwargs):
        if cls is _StackQueue:
            raise TypeError('От этого класса нельзя наследоваться напрямую, используйте субклассы')
        return super().__new__(cls)

    def __init__(self, initlist=None):
        self._items = []

        if initlist is not None:
            for x in initlist:
                self.add(x)

    @property
    def is_empty(self):
        if self._items and len(self._items):
            return False
        return True

    def pop(self):
        if self.is_empty:
            return None
        else:
            return self._items.pop()

    def clear(self):
        del self._items
        self._items = []

    def __len__(self):
        return len(self._items)

    len = property(lambda s: len(s))

    def __str__(self):
        return self.read()


class CharStack(_StackQueue):
    is_stack = True

    def top(self):
        try:
            return self._items[-1]
        except:
            pass
        return ''

    def bottom(self):
        try:
            return self._items[0]
        except:
            pass
        return ''

    def add(self, value):
        self._items.append(str(value))

    def read(self):
        return ''.join(self._items)

    def __iter__(self):
        return self

    def __next__(self):
        x = self.pop()
        if x and x != '':
            return x
        raise StopIteration


class CharQueue(_StackQueue):
    is_stack = False

    def first(self):
        try:
            return self._items[-1]
        except:
            pass
        return ''

    def last(self):
        try:
            return self._items[0]
        except:
            pass
        return ''

    def add(self, value):
        self._items.insert(0, str(value))

    def read(self):
        return ''.join(reversed(self._items))

    def __iter__(self):
        return self

    def __next__(self):
        x = self.pop()
        if x and x != '':
            return x
        raise StopIteration


class VarStack(_StackQueue):
    is_stack = True

    def top(self):
        try:
            return self._items[-1]
        except:
            pass
        return None

    def bottom(self):
        try:
            return self._items[0]
        except:
            pass
        return None

    def add(self, value):
        self._items.append(value)

    def read(self):
        return ''.join(map(repr, self._items))

    def __iter__(self):
        return self

    def __next__(self):
        x = self.pop()
        if x is not None:
            return x
        raise StopIteration


class VarQueue(_StackQueue):
    is_stack = False

    def first(self):
        try:
            return self._items[-1]
        except:
            pass
        return None

    def last(self):
        try:
            return self._items[0]
        except:
            pass
        return None

    def add(self, value):
        self._items.insert(0, value)

    def read(self):
        return ''.join(map(repr, self._items))

    def __iter__(self):
        return self

    def __next__(self):
        x = self.pop()
        if x is not None:
            return x
        raise StopIteration
