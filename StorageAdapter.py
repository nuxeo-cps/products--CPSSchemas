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

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getEngine


class BaseStorageAdapter:
    """Base Storage Adapter

    Base class for storage adapters.
    """

    def __init__(self, schema, field_ids=None):
        """Create a StorageAdapter for a schema.

        If field_ids is specified, only those fields will be managed.
        """
        self._schema = schema
        if field_ids is None:
            field_items = schema.items()
        else:
            field_items = []
            for field_id, field in schema.items():
                if field_id in field_ids:
                    field_items.append((field_id, field))
        self._field_items = field_items

    def getSchema(self):
        """Get schema this adapter is about."""
        return self._schema

    def getFieldItems(self):
        """Get the field ids and the fields."""
        return self._field_items

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

    def _setData(self, data, **kw):
        """Set data to the object, from a mapping."""
        data = self._setDataDoProcess(data, **kw)
        for field_id, field in self.getFieldItems():
            if field.write_ignore_storage:
                continue
            self._setFieldData(field_id, field, data[field_id], **kw)

    def _setDataDoProcess(self, data, **kw):
        """Process data before write.

        Returns a copy.
        """
        new_data = {}
        for field_id, field in self.getFieldItems():
            value = data[field_id]
            new_data[field_id] = field.processValueBeforeWrite(value, data)
        return new_data

    def _setFieldData(self, field_id, field, value, **kw):
        """Set data for one field."""
        raise NotImplementedError


class AttributeStorageAdapter(BaseStorageAdapter):
    """Attribute Storage Adapter

    This adapter simply gets and sets data from/to an attribute.
    """

    def __init__(self, schema, ob, field_ids=None):
        """Create an Attribute Storage Adapter for a schema.

        The object passed is the one on which to get/set attributes.
        """
        self._ob = ob
        BaseStorageAdapter.__init__(self, schema, field_ids=field_ids)

    def setContextObject(self, ob):
        """Set a new underlying object for this adapter.

        If a getData/setData is later done, it will be done on this new
        object.

        This is used by CPS to switch to a writable object after unfreezing.
        """
        self._ob = ob

    def _delete(self, field_id):
        raise NotImplementedError
        # TODO: implement something
        ob = self._ob
        if ob.__dict__.has_key(field_id):
            # Only delete attributes that have been set on the instance.
            delattr(ob, field_id)
        else:
            LOG('AttributeStorageAdapter._delete', DEBUG,
                'Attempting to delete %s on %s' % (field_id, ob))

    def _getFieldData(self, field_id, field):
        """Get data from one field."""
        ob = self._ob
        if not hasattr(aq_base(ob), field_id):
            # Use default from field.
            return field.getDefault()
        return getattr(ob, field_id)

    def _setFieldData(self, field_id, field, value):
        """Set data for one field."""
        setattr(self._ob, field_id, value)

    def _getContentUrl(self, object, field_id):
        return '%s/%s' % (object.absolute_url(), field_id)


class MetaDataStorageAdapter(BaseStorageAdapter):
    """MetaData Storage Adapter

    This adapter simply gets and sets metadata using X() and setX() methods
    """

    def __init__(self, schema, ob, field_ids=None):
        self._ob = ob
        BaseStorageAdapter.__init__(self, schema, field_ids=field_ids)

    def setContextObject(self, ob):
        """Set a new underlying object for this adapter."""
        self._ob = ob

    def _delete(self, field_id):
        raise NotImplementedError

    def _getFieldData(self, field_id, field):
        """Get data from one field.

        Calls the getter method.
        """
        ob = self._ob
        if not hasattr(aq_base(ob), field_id):
            # Use default from field.
            return field.getDefault()

        meth = getattr(ob, field_id)
        if callable(meth):
            return meth()
        return meth

    def _setFieldData(self, field_id, field, value):
        """Set data for one field.

        Calls the setter method.
        """
        ob = self._ob
        if field_id in ('Coverage', 'Source', 'Relation'):
            # finish the CMF Dublin Core implementation
            # storing these metadata as attributes
            setattr(ob, field_id, value)
            return
        meth_name = 'set' + field_id
        if not hasattr(aq_base(ob), meth_name):
            # skip metadata without setter method
            LOG('MetaDataStorageAdapter._setFieldData', ERROR,
                "Warning no method %s(), field not saved" % meth_name)
            return
        meth = getattr(ob, meth_name)
        if not callable(meth):
            raise ValueError(
                "Invalid MetaData field, %s not callable" % meth_name)
        meth(value)

    def _getContentUrl(self, object, field_id):
        return '%s/%s' % (object.absolute_url(), field_id)
