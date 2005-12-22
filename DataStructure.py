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

from copy import deepcopy
from UserDict import UserDict

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CPSUtil.file import persistentFixup
from ZPublisher.HTTPRequest import FileUpload

from Products.CPSSchemas.Widget import widgetname
from Products.CPSUtil.session import sessionHasKey

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

    def clear(self):
        self.data.clear()
        self.clearErrors()

    def clearErrors(self):
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
        """Update field data from a mapping.

        This method (unlike the standard update method) will only update
        existing fields. It is used to set the data from request (or indeed
        any other object with a mapping-interface).

        No validation is done.

        Empty FileUpload values are treated as absent.
        """
        for key in self.keys():
            wkey = widgetname(key) # mapping contains full widget names
            if mapping.has_key(wkey):
                value = mapping[wkey]
                if isinstance(value, FileUpload) and not value:
                    # Don't overwrite with an empty FileUpload
                    continue
                self[key] = value

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

    def getDataModel(self):
        """Return the datamodel associated with this datastructure."""
        return self.datamodel

    def _getAllData(self):
        """Get a non-persistent copy of this datastructure with all info.

        Fixes up FileUploads to be correctly persistable in the session.
        """
        data = persistentFixup(self.data) # fixup FileUploads
        return deepcopy((data, self.errors, self.error_mappings))

    def _updateAllData(self, data):
        data, errors, error_mappings = deepcopy(data)
        for key, value in data.items():
            if isinstance(value, FileUpload) and not value:
                # Don't overwrite with an empty FileUpload
                continue
            self.data[key] = value
        self.errors.update(errors)
        self.error_mappings.update(error_mappings)

    def _saveToSession(self, request, formuid):
        """Save this datastructure into the session.

        Uses ``formuid`` to identify the form.
        """
        if request is None:
            return
        data = self._getAllData()
        request.SESSION[_SESSION_DATASTRUCTURE_KEY] = formuid, data

    def _updateFromSession(self, request, formuid):
        """Update this datastructure from the session.

        Uses ``formuid`` to identify the form.
        """
        if not sessionHasKey(request, _SESSION_DATASTRUCTURE_KEY):
            return
        dataformuid, data = request.SESSION[_SESSION_DATASTRUCTURE_KEY]
        if dataformuid != formuid:
            return
        self._updateAllData(data)

    def _removeFromSession(self, request):
        """Remove saved data for this datastructure from the session.
        """
        if not sessionHasKey(request, _SESSION_DATASTRUCTURE_KEY):
            return
        del request.SESSION[_SESSION_DATASTRUCTURE_KEY]

InitializeClass(DataStructure)
