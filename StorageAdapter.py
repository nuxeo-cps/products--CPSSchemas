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

"""
Storage Adapters

A storage adapter is used by a DataModel to get/set the data from/to
somewhere. It is is parameterised on one hand by some context, for
instance an object, and on the other hand by the schema that drives it.

A storage adapter can also be linked to no object, for instance for
object creation.

The most basic implementation is using attributes on an object. A more
complex one can be a storage to an SQL table. Another one could be a
setting of attributes in the ZODB that knows about File and Image fields
and makes them available as subobjects so that they are visible in the
ZMI.

"""

from zLOG import LOG, DEBUG
from Acquisition import aq_base
from Missing import MV # Missing.Value


class BasicStorageAdapter:
    """Basic Storage Adapter

    Base class for storage adapters.
    """

    def __init__(self, schema):
        """Create a StorageAdapter for a schema."""
        self._schema = schema

    #
    # Internal methods to be implemented for simple cases.
    #

    def _get(self, field_id):
        """Get the value for one field."""
        raise NotImplementedError

    def _set(self, field_id, value):
        """Set the value into one field."""
        raise NotImplementedError

    def _delete(self, field_id):
        """Delete a field."""
        # XXX this is useful for flex docs when the schema changes.
        raise NotImplementedError

    #
    # API called by DataModel
    #

    def getData(self):
        """Get data from the object, returns a mapping.

        The values returned may be Missing.Value if they're not found.
        """
        data = {}
        for field_id in self._schema.keys():
            data[field_id] = self._get(field_id)
        return data

    def setData(self, data):
        """Set data to the object, from a mapping.

        If the value is Missing.Value, nothing is done for this field.
        """
        for field_id in self._schema.keys():
            self._set(field_id, data[field_id])


class AttributeStorageAdapter(BasicStorageAdapter):
    """Attribute Storage Adapter

    This adapter simply gets and sets data from/to an attribute.
    """

    def __init__(self, schema, ob):
        """Create an Attribute Storage Adapter for a schema.

        The object passed is the one on which to get/set attributes.
        """
        self._ob = ob
        BasicStorageAdapter.__init__(self, schema)

    def setContextObject(self, ob):
        """Set a new underlying object for this adapter.

        If a getData/setData is later done, it will be done on this new
        object.

        This is used by CPS to switch to a writable object after unfreezing.
        """
        self._ob = ob

    def _get(self, field_id):
        """Get the value or returns Missing.Value."""
        ob = self._ob
        if hasattr(aq_base(ob), field_id):
            return getattr(ob, field_id)
        else:
            return MV

    def _set(self, field_id, value):
        """Set the value except if it's Missing.Value."""
        ob = self._ob
        if value is not MV:
            setattr(ob, field_id, value)
        else:
            LOG('AttributeStorageAdapter._set', DEBUG,
                'Setting MV for %s on %s' % (field_id, ob))

    def _delete(self, field_id):
        raise NotImplementedError
        ob = self._ob
        if ob.__dict__.has_key(field_id):
            # Only delete attributes that have been set on the instance.
            delattr(ob, field_id)
        else:
            LOG('AttributeStorageAdapter._delete', DEBUG,
                'Attempting to delete %s on %s' % (field_id, ob))

