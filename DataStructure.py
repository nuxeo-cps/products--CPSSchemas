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
"""DataStructure

A DataStructure holds the form-related data before display or after
validation returned an error, for redisplay.
"""

# NOTE: this text is old
# Data structures are classes that hold the content of a document while it is
# being used. It is NOT a storage, it's not persistent at all. It's purpose is:
# - Keeping track of which fields have changed, so that StorageAdapters only
#   need to update fields/tables that have been modified.
#
# Required vs non-required fields and default data behaviour
# ==========================================================
# That a field is required mean that it must have some data and that this data
# may not be None. So, None and non-existing means the same thing (this may
# seem obvious, but it isn't). An empty string and None is NOT the same however,
# which means that string fields will have to have separate settings for if it
# is required and if an empty string is allowed.
# A field may have default data. In fact, all fields have a default setting,
# but it is set to None by default. We find that there are four combinations
# of these settings:
# a: A required field with no default value
# b: A required field with default value
# c: A non-required field with no default value
# d: A non-required field with default value
# There are two different cases when both these settings in combination modify
# the fields behaviour:
# 1. When a field is set/validated with None
# 2. When a fields create view is displayed
#
# a: It is clear that if the field is required and no default is set, data must
# be submitted when the field is set/validated, or an validation error should
# occur.
# b: A required field that has a default value should return the default value
# when validation occurs with None or non-existant values.
# c. A non-required field with no default value and no requested value should
# not exist. If such a field exists, and is then set to None, it should be
# removed, or in cases where removing is not possible (such as in SQL tables) it
# should be set to None/NULL/NIL.
# d. This is less clear, but it should reasonably be set to None, or it will be
# impossible to set it to None, thereby in effect making it required. However,
# this field behaves differently from fields of type c when created, since the
# initial value shown in the creation form will contain the default value. It
# also behaves differently from type b fields, since you can remove the value
# before creation.
#
# This is all quite simple, but it took me a whole afternoon to get it straight,
# so the text should stay, so I don't get confused once again. :) /regebro

from UserDict import UserDict

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CPSDocument.Widget import widgetname


class DataStructure(UserDict):
    """Used for passing a documents data and validation errors around

    It's basically two dictionaries, one for data and one for errors.
    The data dictionary is exposed through the standard dictionary interface,
    while the error dictionary is exposed through a set of methods.
    Bugs/features:
    - comparisons will not take errors into account
    - __setitem__ only updates the data, the errors will stay unchanged,
      no validation will occur. We COULD change this so validation occurs
      with setitem, and to set without validation you operate directly on
      DataStructure.data. It's mostly a matter of tatse, and I can't decide. :)"""

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, data={}, errors={}):
        self.data = {}
        self.data.update(data)
        self.errors = {}
        self.errors.update(errors)

    # Override standard dictionary stuff:
    def clear(self):
        self.data.clear()
        self.errors.clear()

    def __delitem__(self, key):
        del self.data[key]
        if self.errors.has_key(key):
            del self.errors[key]

    def copy(self):
        if self.__class__ is DataStructure:
            return DataStructure(self.data, self.errors)
        # Some kind of subclass. Just return a dict with data.
        # If more is needed, override copy() in the subclass.
        return self.data.copy()

    def popitem(self):
        key, val = self.data.popitem()
        if self.errors.has_key(key):
            del self.errors[key]
        return key, val

    def update(self, dict):
        if isinstance(dict, UserDict):
            self.data.update(dict.data)
        elif isinstance(dict, type(self.data)):
            self.data.update(dict)
            # XXX do same for errors
        else:
            for k, v in dict.items():
                self.data[k] = v

    def updateFromMapping(self, mapping):
        """Updates and validates field data from a mapping.

        This method (unlike the standard update method) will only update
        existing fields. It is used to set the data from request (or indeed
        any other object with a mapping-interface).

        No validation is done.
        """
        for key in self.keys():
            if mapping.has_key(widgetname(key)):
                self[key] = mapping[widgetname(key)]

    # Expose setter as method for restricted code.
    def set(self, key, value):
        self.__setitem__(key, value)

    # Expose the errors dictionary.
    def getError(self, key):
        return self.errors.get(key)

    def hasError(self, key):
        return self.errors.has_key(key)

    def setError(self, key, message):
        self.errors[key] = message

    def delError(self, key):
        """Removes an error"""
        if self.errors.has_key(key):
            del self.errors[key]

    def getErrorsFields(self):
        return self.errors.keys()

    def getErrors(self):
        return self.errors # XXX Should it return the original or a copy?

InitializeClass(DataStructure)
