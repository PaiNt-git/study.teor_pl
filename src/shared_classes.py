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

    def is_empty(self):
        if self._items and len(self._items):
            return False
        return True

    def pop(self):
        if self.is_empty():
            return ''
        else:
            return self._items.pop()

    def clear(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    len = property(lambda s: len(s))

    def __str__(self):
        return self.show_all_as_str()


class CharStack(_CharStackQueue):
    is_stack = True

    def add(self, value):
        self._items.append(str(value))

    def show_all_as_str(self):
        return ''.join(self._items)


class CharQueue(_CharStackQueue):
    is_stack = False

    def add(self, value):
        self._items.insert(0, str(value))

    def show_all_as_str(self):
        return ''.join(reversed(self._items))
