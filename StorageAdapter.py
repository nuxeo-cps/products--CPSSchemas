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

from zLOG import LOG, DEBUG, ERROR
from Acquisition import aq_base

class BaseStorageAdapter:
    """Base Storage Adapter

    Base class for storage adapters.
    """

    def __init__(self, schema, field_ids=None, **kw):
        """Create a StorageAdapter for a schema.

        If field_ids is specified, only those fields will be managed.
        """
        self._schema = schema
        if field_ids is None:
            field_ids = schema.keys()
        field_items = []
        writable_field_items = []
        for field_id, field in schema.items():
            if field_id in field_ids:
                field_items.append((field_id, field))
                if not field.write_ignore_storage:
                    writable_field_items.append((field_id, field))
        self._field_items = field_items
        self._writable_field_items = writable_field_items

    def setContextObject(self, context):
        """Set a new underlying context for this adapter.

        If a getData/setData is later done, it will be done on this new
        context.

        This is used by CPS to switch to a writable object after unfreezing.
        Also used by directory entry creation process, to specifiy the
        id after an empty datamodel has been fetched.
        """
        raise NotImplementedError

    def getSchema(self):
        """Get schema this adapter is about."""
        return self._schema

    def getFieldItems(self):
        """Get the field ids and the fields."""
        return self._field_items

    def getFieldIds(self):
        return [field_id for field_id, field in self.getFieldItems()]

    def getWritableFieldItems(self):
        """Get the writable field ids and the fields."""
        return self._writable_field_items

    def getDefaultData(self):
        """Get the default data from the fields' default values.

        Returns a mapping.
        """
        data = {}
        for field_id, field in self.getFieldItems():
            data[field_id] = field.getDefault()
        return data

    #
    # API called by DataModel
    #
    def getData(self):
        """Get data from the object, returns a mapping."""
        return self._getData()

    def setData(self, data):
        """Set data to the object, from a mapping."""
        self._setData(data)

    #
    # Internal API for subclasses
    #
    def _getData(self, **kw):
        """Get data from the object, returns a mapping."""
        data = {}
        for field_id, field in self.getFieldItems():
            if field.read_ignore_storage:
                value = field.getDefault()
            else:
                value = self._getFieldData(field_id, field, **kw)
            data[field_id] = value
        self._getDataDoProcess(data, **kw)
        return data

    def _getDataDoProcess(self, data, **kw):
        """Process data after read."""
        for field_id, field in self.getFieldItems():
            value = data[field_id]
            data[field_id] = field.processValueAfterRead(value, data)

    def _getFieldData(self, field_id, field, **kw):
        """Get data from one field."""
        raise NotImplementedError

    def _setData(self, data):
        """Set data to the object, from a mapping."""
        data = self._setDataDoProcess(data)
        for field_id, field in self.getWritableFieldItems():
            self._setFieldData(field_id, data[field_id])

    def _setDataDoProcess(self, data):
        """Process data before write.

        Returns a copy, without the fields that are not stored."""
        new_data = {}
        for field_id, field in self.getFieldItems():
            if field.write_ignore_storage:
                continue
            value = data[field_id]
            new_data[field_id] = field.processValueBeforeWrite(value, data)
        return new_data

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        raise NotImplementedError


class AttributeStorageAdapter(BaseStorageAdapter):
    """Attribute Storage Adapter

    This adapter simply gets and sets data from/to an attribute.
    """

    def __init__(self, schema, ob, **kw):
        """Create an Attribute Storage Adapter for a schema.

        The object passed is the one on which to get/set attributes.
        """
        self._ob = ob
        BaseStorageAdapter.__init__(self, schema, **kw)

    def setContextObject(self, context):
        """Set a new underlying context for this adapter."""
        self._ob = context

    def _getFieldData(self, field_id, field):
        """Get data from one field."""
        ob = self._ob
        if not hasattr(aq_base(ob), field_id):
            # Use default from field.
            return field.getDefault()
        return getattr(ob, field_id)

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        # No kw arguments are expected.
        setattr(self._ob, field_id, value)

    def _getContentUrl(self, object, field_id, file_name):
        return '%s/downloadFile/%s/%s' % (
            object.absolute_url(), field_id, file_name)


ACCESSOR = []
ACCESSOR_READ_ONLY = []

class MetaDataStorageAdapter(BaseStorageAdapter):
    """MetaData Storage Adapter

    This adapter simply gets and sets metadata using X() and setX() methods for
    standard CMF Dublin Core methods, or using specific attributes otherwise.
    """

    _field_attributes = {
        'Creator': ACCESSOR_READ_ONLY,
        'CreationDate': ACCESSOR_READ_ONLY,
        'Title': ACCESSOR,
        'Subject': ACCESSOR,
        'Description': ACCESSOR,
        'Contributors': ACCESSOR,
        'ModificationDate': ACCESSOR,
        'EffectiveDate': ACCESSOR,
        'ExpirationDate': ACCESSOR,
        'Format': ACCESSOR,
        'Language': ACCESSOR,
        'Rights': ACCESSOR,
        # XXX move these to accessors too using a monkey-patch.
        'Coverage': 'coverage',
        'Source': 'source',
        'Relation': 'relation',
        }

    def __init__(self, schema, ob, **kw):
        self._ob = ob
        BaseStorageAdapter.__init__(self, schema, **kw)

    def setContextObject(self, context):
        """Set a new underlying context for this adapter."""
        self._ob = context

    def _getFieldData(self, field_id, field):
        """Get data from one field.

        Calls the getter method.
        """
        ob = self._ob
        if ob is None:
            # Creation
            return field.getDefault()
        attr = self._field_attributes.get(field_id)
        if attr is None:
            raise ValueError("Field %s not allowed by MetaDataStorageAdapter"
                             % field_id)
        elif attr is ACCESSOR or attr is ACCESSOR_READ_ONLY:
            return getattr(ob, field_id)()
        elif hasattr(aq_base(ob), attr):
            return getattr(ob, attr)
        else:
            # Use default from field.
            return field.getDefault()

    def _setFieldData(self, field_id, value):
        """Set data for one field.

        Calls the setter method.
        """
        # No kw arguments are expected.
        ob = self._ob
        attr = self._field_attributes.get(field_id)
        if attr is None:
            raise ValueError("Field %s not allowed by MetaDataStorageAdapter"
                             % field_id)
        elif attr is ACCESSOR:
            getattr(ob, 'set'+field_id)(value)
        elif attr is ACCESSOR_READ_ONLY:
            raise ValueError("Field %s is read-only" % field_id)
        else:
            setattr(ob, attr, value)


class MappingStorageAdapter(BaseStorageAdapter):
    """Mapping or dictionnary Storage Adapter

    This adapter simply store data into a dictionnary.
    """

    def __init__(self, schema, ob, **kw):
        """Create an Attribute Storage Adapter for a schema.

        The object passed is the one on which to get/set attributes.
        """
        self._ob = ob
        BaseStorageAdapter.__init__(self, schema, **kw)

    def setContextObject(self, context):
        """Set a new underlying context for this adapter."""
        pass

    def _getFieldData(self, field_id, field):
        """Get data from one field."""
        LOG('XXXX getFieldData', DEBUG, 'get %s' % field_id)
        return self._ob.get(field_id, field.getDefault())

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        # No kw arguments are expected.
        self._ob.update({field_id : value})
