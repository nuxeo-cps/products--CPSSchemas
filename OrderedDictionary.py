# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# An Ordered, Persistent dictionary.
# Some code from David Benjamins odict
# $Id$

from types import ListType, TupleType
from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList

class OrderedDictionary(PersistentMapping):
    def __init__(self, dict = None):
        if dict:
            self._keys = PersistentList(dict.keys())
        else:
            self._keys = PersistentList()
        PersistentMapping.__init__(self, dict)

    def __delitem__(self, key):
        PersistentMapping.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        PersistentMapping.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def __cmp__(self, dict):
        if isinstance(dict, OrderedDictionary):
            return cmp(self.data, dict.data) and cmp(self._keys, dict._keys)
        else:
            return 0

    def clear(self):
        PersistentMapping.clear(self)
        self._keys = PersistentList()

    def copy(self):
        mcopy = OrderedDictionary()
        mcopy.data = self.data.copy()
        mcopy._keys = self._keys[:]
        return mcopy

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys[:] # This returns a non-persistent copy of self._keys,
                             # so you can manipulate the copy without manipulating self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def index(self, key):
        return self._keys.index(key)

    def setdefault(self, key, failobj = None):
        if key not in self._keys: self._keys.append(key)
        return PersistentMapping.setdefault(self, key, failobj)

    def update(self, dict):
        for (key,val) in dict.items():
            self.__setitem__(key,val)

    def values(self):
        return map(self.get, self._keys)

    def order(self, key, order ):
        """Moves the specified item to the specifed position

        0 is first, 1 is second, -1 is last, -1 second from last, and so on.
        """
        if order < 0:
            order = len(self) + order # Negative numbers are counted from behind
        if order < 0:
            order = 0 # It's still negative: move first
        self._keys.remove(key)
        if order >= len(self._keys):
            self._keys.append(key)
        else:
            self._keys.insert(order, key)

    def move(self, key, distance):
        """Moves the specified item a number of positions

        Positive numbers move to higher index numbers, negavtive to lower index numbers"""
        oldpos = self.index(key)
        newpos = oldpos + distance
        if newpos < 0:
            newpos = 0
        self.order(key, newpos)




