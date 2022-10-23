'''
Created on 2 окт. 2022 г.

@author: PaiNt
'''


class _CharStackQueue:

    def __new__(cls, *args, **kwargs):
        if cls is _CharStackQueue:
            raise TypeError('От этого класса нельзя наследоваться напрямую, используйте субклассы')
        return super().__new__(cls)

    def __init__(self, initlist=None):
        self._items = []

        if initlist is not None:
            for x in initlist:
                self.add(str(x))

    @property
    def is_empty(self):
        if self._items and len(self._items):
            return False
        return True

    def pop(self):
        if self.is_empty:
            return ''
        else:
            return self._items.pop()

    def clear(self):
        del self._items
        self._items = []

    def __len__(self):
        return len(self._items)

    len = property(lambda s: len(s))

    def __str__(self):
        return self.show_all_as_str()


class CharStack(_CharStackQueue):
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
        if x != '':
            return x
        raise StopIteration


class CharQueue(_CharStackQueue):
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
        if x != '':
            return x
        raise StopIteration
