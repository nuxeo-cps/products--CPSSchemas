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

from UserDict import UserDict

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CPSSchemas.Widget import widgetname


class DataStructure(UserDict):
    """An abstraction for the data entered by the user or displayed.

    It also stores error messages if the data cannot be validated.

    It also stores the datamodel backing this datastructure.

    It's basically two dictionaries, one for data and one for errors.
    The data dictionary is exposed through the standard dictionary
    interface, while the error dictionary is exposed through specific
    methods.
    """
    # Bugs/features:
    # - __setitem__ only updates the data, the errors will stay
    #   unchanged.

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, data={}, errors={}, datamodel=None):
        self.data = {}
        self.data.update(data)
        self.errors = {}
        self.errors.update(errors)
        self.datamodel = datamodel

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

        XXX: explain why <widgetname(key)> is used instead of <key>.
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

    # XXX: Not used, seemingly
    def delError(self, key):
        """Removes an error"""
        if self.errors.has_key(key):
            del self.errors[key]

    # XXX: Not used, seemingly
    def getErrorsFields(self):
        return self.errors.keys()

    # XXX: Not used, seemingly
    def getErrors(self):
        return self.errors # XXX Should it return the original or a copy?

    def getDataModel(self):
        """Return the datamodel associated with this datastructure."""
        return self.datamodel


InitializeClass(DataStructure)
