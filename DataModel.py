# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""DataModel

The DataModel is a transient object that holds information about a
particular document's data structure, including the underlying schemas
and the storage options.

It is *not* a storage, it isn't persistent at all. Its purpose is:

- being one single point of access for information on the structure of
  the document, as well as a single point of access for the document
  data, no matter with which schema and in which storage the data is
  located,

- validating data before storage,

- acting as a cache (read and write) for data. This is only really
  useful for data that is not stored in the ZODB, but for simplicity
  *all* data is cached. (NOTIMPLEMENTED).

The storage itself is done through a storage adapter (NOTIMPLEMENTED).
"""

from zLOG import LOG, DEBUG
from Acquisition import aq_base
from UserDict import UserDict

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


class ValidationError(Exception):
    """Validation error during field storage."""
    pass


class DataModel(UserDict):
    """An abstraction for the data stored in an object.
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, ob, schemas=[]):
        UserDict.__init__(self)
        self._ob = ob
        self._fields = {}
        self._schemas = {}
        for schema in schemas:
            self._addSchema(schema)

    def getObject(self):
        """Get the object this DataModel is about."""
        return self._ob

    # Expose setter as method for restricted code.
    def set(self, key, value):
        # XXX This should check field permission access...
        self.__setitem__(key, value)

    def _addSchema(self, schema):
        for fieldid in schema.keys():
            if self._fields.has_key(fieldid):
                raise KeyError("Two schemas have field id %s "
                               " but field ids must be unique" % fieldid)
            else:
                self._fields[fieldid] = schema[fieldid]
        self._schemas[schema.id] = schema

    def _fetch(self):
        """Fetch the data into local dict for user access."""
        for schema in self._schemas.values():
            # XXX use storage adapters for each schema
            for fieldid in schema.keys():
                try:
                    v = getattr(aq_base(self._ob), fieldid)
                except AttributeError:
                    field = schema[fieldid]
                    v = field.getDefault()
                self.data[fieldid] = v

    def _commit(self):
        """Commit modified data into object."""
        ob = self._ob
        for schema in self._schemas.values():
            # XXX use storage adapters for each schema
            for fieldid in schema.keys():
                setattr(ob, fieldid, self.data[fieldid])
        # XXX temporary until we have a better API for this
        if hasattr(aq_base(ob), 'postCommitHook'):
            ob.postCommitHook()


    def __repr__(self):
        return '<DataModel %s>' % (self.data,)

InitializeClass(DataModel)
