# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Authors: Lennart Regebro <lr@nuxeo.com>
#          Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
#
# Some of this code is inspired from David Benjamin's odict.
"""
An ordered, persistent dictionary.
"""

from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList

def _isinstance(ob, cls):
    try:
        return isinstance(ob, cls)
    except TypeError:
        # In python 2.1 isinstance() raises TypeError
        # instead of returning 0 for ExtensionClasses.
        return 0


class OrderedDictionary(PersistentMapping):
    def __init__(self, dict=None):
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
        if key not in self._keys:
            self._keys.append(key)

    # ExtensionClass uses __cmp__ instead of __eq__ for == ...
    def __cmp__(self, dict):
        if _isinstance(dict, OrderedDictionary):
            # XXX fix this
            return cmp(self.data, dict.data) and cmp(self._keys, dict._keys)
        else:
            return 1

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
        return self._keys[:]

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

    def setdefault(self, key, failobj=None):
        if key not in self._keys:
            self._keys.append(key)
        return PersistentMapping.setdefault(self, key, failobj)

    def update(self, dict):
        for (key, val) in dict.items():
            self.__setitem__(key,val)

    def values(self):
        return map(self.get, self._keys)

    def order(self, key, order):
        """Move the specified item to the specifed position.

        0 is first, 1 is second, ...
        -1 is last, -2 is second from last, ...
        """
        if order < 0:
            order = len(self._keys) + order
            if order < 0:
                order = 0
        self._keys.remove(key)
        if order >= len(self._keys):
            self._keys.append(key)
        else:
            self._keys.insert(order, key)

    def move(self, key, distance):
        """Move the specified item a number of positions.

        Positive numbers move to higher index numbers,
        negative to lower index numbers.
        """
        newpos = self.index(key) + distance
        if newpos < 0:
            newpos = 0
        self.order(key, newpos)
