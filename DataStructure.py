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

from Products.CPSSchemas.utils import untieFromDatabase
from Products.CPSSchemas.Widget import widgetname

_SESSION_DATASTRUCTURE_KEY = 'CPS_DATASTRUCTURE'


class DataStructure(UserDict):
    """An abstraction for the data entered by the user or displayed.

    It also stores error messages if the data cannot be validated.

    It also stores the datamodel backing this datastructure.

    It's basically two dictionaries, one for data and one for errors.
    The data dictionary is exposed through the standard dictionary
    interface, while the error dictionary is exposed through specific
    methods. There are actually two dictionaries for the errors, as
    we may want to store a mapping of variable -> value.
    """
    # Bugs/features:
    # - __setitem__ only updates the data, the errors will stay
    #   unchanged.

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, data={}, errors={}, error_mappings={}, datamodel=None):
        self.data = {}
        self.data.update(data)
        self.errors = {}
        self.errors.update(errors)
        self.error_mappings = {}
        self.error_mappings.update(errors)
        self.datamodel = datamodel

    # Override standard dictionary stuff:
    def clear(self):
        self.data.clear()
        self.errors.clear()
        self.error_mappings.clear()

    def __delitem__(self, key):
        del self.data[key]
        if self.errors.has_key(key):
            del self.errors[key]
        if self.error_mappings.has_key(key):
            del self.error_mappings[key]

    def copy(self):
        if self.__class__ is DataStructure:
            return DataStructure(self.data, self.errors, self.error_mappings)
        # Some kind of subclass. Just return a dict with data.
        # If more is needed, override copy() in the subclass.
        return self.data.copy()

    def popitem(self):
        key, val = self.data.popitem()
        if self.errors.has_key(key):
            del self.errors[key]
        if self.error_mappings.has_key(key):
            del self.error_mappings[key]
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
        #raise "mapping", str(mapping)
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

    def setError(self, key, message, mapping=None):
        self.errors[key] = message
        self.error_mappings[key] = mapping

    def getErrorMapping(self, key):
        return self.error_mappings.get(key) or {}

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

    def _getAllData(self):
        """Get a non-persistent copy with all info.

        Needed because persistent objects like Files stored in a session
        must not be tied to a database.
        """
        data = {}
        errors = {}
        error_mappings = {}
        for key, value in self.data.items():
            data[key] = untieFromDatabase(value)
        for key, value in self.errors.items():
            errors[key] = untieFromDatabase(value)
        for key, value in self.error_mappings.items():
            error_mappings[key] = untieFromDatabase(value)
        return (data, errors, error_mappings)

    def _setAllData(self, data):
        data, errors, error_mappings = data
        self.data = {}
        self.errors = {}
        self.error_mappings = {}
        for key, value in data.items():
            self.data[key] = untieFromDatabase(value)
        for key, value in errors.items():
            self.errors[key] = untieFromDatabase(value)
        for key, value in error_mappings.items():
            self.error_mappings[key] = untieFromDatabase(value)

    def _saveToSession(self, request):
        """Save this datastructure into the session.
        """
        if request is None:
            return
        data = self._getAllData()
        request.SESSION[_SESSION_DATASTRUCTURE_KEY] = data

    def _loadFromSession(self, request):
        """Load this datastructure from the session.
        """
        if request is None:
            return
        # XXX don't create a new session if none is present,
        # be more subtle by checking request._lazies and request.other
        # for a SESSION key.
        if not request.SESSION.has_key(_SESSION_DATASTRUCTURE_KEY):
            return
        data = request.SESSION[_SESSION_DATASTRUCTURE_KEY]
        if data is None:
            return
        # XXX should have some sanity checks about schemas etc.
        self._setAllData(data)

    def _removeFromSession(self, request):
        """Remove saved data for this datastructure from the session.
        """
        if request is None:
            return
        # XXX don't create a new session if none is present,
        # be more subtle by checking request._lazies and request.other
        # for a SESSION key.
        if not request.SESSION.has_key(_SESSION_DATASTRUCTURE_KEY):
            return
        del request.SESSION[_SESSION_DATASTRUCTURE_KEY]

InitializeClass(DataStructure)
