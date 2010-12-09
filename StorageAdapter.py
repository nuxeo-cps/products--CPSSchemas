# (C) Copyright 2003-2006 Nuxeo SAS <http://nuxeo.com>
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

import logging
import warnings
import urllib
from Acquisition import aq_base

from Products.CPSSchemas.BasicFields import CPSSubObjectsField
from Products.CPSSchemas.DataModel import DEFAULT_VALUE_MARKER
from interfaces import IFileField

logger = logging.getLogger(__name__)

def deprecate_getContentUrl():
    warnings.warn('_getContentUrl() is deprecated and will be removed in '
                  'CPS 3.6. Use DataModel.getSubContentUri() instead',
                  DeprecationWarning, stacklevel=2)

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
        write_dependencies = {} # field id -> fields depending on it for write
        all_dependents = [] # fields that depend for write on all others
        for field_id, field in schema.items():
            if field_id in field_ids:
                field_items.append((field_id, field))
                if not field.write_ignore_storage:
                    writable_field_items.append((field_id, field))
                if not field.write_process_expr:
                    continue
                wpdf = field.write_process_dependent_fields
                if '*' in wpdf:
                    all_dependents.append(field_id)
                    continue
                for ancestor in wpdf:
                    write_dependencies.setdefault(ancestor, set()).add(
                        field_id)

        self._field_items = field_items
        self._writable_field_items = writable_field_items
        self._write_dependencies = write_dependencies
        self._all_dependents = all_dependents

    def getContextObject(self):
        """Get the underlying context for this adapter.

        See setContextObject for the semantics.
        """
        return None

    def setContextObject(self, context, proxy=None):
        """Set a new underlying context for this adapter.

        If a getData/setData is later done, it will be done on this new
        context.

        This is used by CPS to switch to a writable object after unfreezing.
        Also used by directory entry creation process, to specifiy the
        id after an empty datamodel has been fetched.
        """
        raise NotImplementedError

    def getProxy(self):
        """Get the potentially associated proxy for this adapter.
        """
        return None

    def getSchema(self):
        """Get schema this adapter is about."""
        return self._schema

    def getFieldItems(self):
        """Get the field ids and the fields."""
        return self._field_items

    def getFieldIds(self):
        return [field_id for field_id, field in self.getFieldItems()]

    def getReadableFieldIds(self):
        return [field_id for field_id, field in self.getFieldItems()
                if not field.read_ignore_storage]

    def getWritableFieldItems(self):
        """Get the writable field ids and the fields."""
        return self._writable_field_items

    def getDefaultData(self):
        """Get the default data from the fields' default values.

        Returns a mapping.
        """
        data = {}
        for field_id in self.getFieldIds():
            data[field_id] = DEFAULT_VALUE_MARKER
        return data

    def finalizeDefaults(self, data, datamodel=None):
        """This has to be called after getData to finalize default values.
        Return the set of fields ids that had to be updated
        """
        changed = set()
        for field_id, v in data.items():
            if v is DEFAULT_VALUE_MARKER:
                data[field_id] = self._schema[field_id].getDefault(datamodel)
                changed.add(field_id)
        return changed

    #
    # API called by DataModel
    #
    def getData(self, field_ids=None):
        """Get data from the object, returns a mapping."""
        return self._getData(field_ids=field_ids)

    def setData(self, data, toset=None):
        """Set data to the object, from a mapping.

        The optional toset argument allows to restrict the data to be written.
        It is a subset of data.keys(). Note that write expressions might need
        the full set of data, possibly even associated to another schema than
        the current adapter takes care of.

        This method has the side effect of updating 'toset' to take write
        dependencies into account.
        """
        try:
            self._setData(data, toset=toset)
        except TypeError:
            # BBB for old subclasses for which _setData has no kwarg
            import sys
            if sys.exc_info()[2].tb_next is not None:
                # error is deeper
                raise
            self._setData(data)

    def getSubContentUri(self, field_id, absolute=False):
        """Return a valid URI for sub content (typically an attached file).

        If no applicable URI can be generated, the returned value is None.
        Example: MappingStorageAdapter working on a purely transient dict.

        If absolute is False, a relative URI with absolute path is generated
        If absolute is True, a full blown absolute URI is generated.

        Exceptions: KeyError in case the field is unknown
                    ValueError in case the field type is inappropriate
                               (currently if it doesn't provide IFileField)
        """
        field = self._schema[field_id]
        if not IFileField.providedBy(field):
            raise ValueError("Not a IFileField: %r", field_id)

        return self._getSubContentUri(field_id, field, absolute=absolute)

    #
    # Internal API for subclasses
    #

    def _getSubContentUri(self, field_id, field, absolute=False):
        """Concrete implementation at subclass level for getSubContentUri().

        Check getSubContentUri() doc for details.
        """
        return None # means not applicable to current adapter

    def _getWriteProcessFieldIds(self):
        res = set()

        for field_id, field in self.getFieldItems():
            if not field.write_process_expr:
                continue
            res.add(field_id)
            wpdf = field.write_process_dependent_fields
            if '*' in wpdf:
                return self.getFieldIds()
            res.update(wpdf)
        return res

    def _getData(self, field_ids=None, **kw):
        """Get data from the object, returns a mapping."""
        data = {}
        for field_id, field in self.getFieldItems():
            if field_ids is not None and not field_id in field_ids:
                continue
            if field.read_ignore_storage:
                value = DEFAULT_VALUE_MARKER
            else:
                value = self._getFieldData(field_id, field, **kw)
            data[field_id] = value
        self._getDataDoProcess(data, field_ids=field_ids, **kw)
        return data

    def _getDataDoProcess(self, data, field_ids=None, **kw):
        """Process data after read."""
        for field_id, field in self.getFieldItems():
            if field_ids is not None and field_id not in field_ids:
                continue
            value = data[field_id]
            data[field_id] = field.processValueAfterRead(value, data,
                                                         self.getContextObject(),
                                                         self.getProxy())

    def _getFieldData(self, field_id, field, **kw):
        """Get data from one field."""
        raise NotImplementedError

    def _setData(self, data, toset=None):
        """Set data to the object, from a mapping.

        Only data  belonging to 'toset' and dependencies will be written."""
        data = self._setDataDoProcess(data, toset=toset)
        for field_id, field in self.getWritableFieldItems():
            if not data.has_key(field_id):
                continue
            self._setFieldData(field_id, data[field_id])

    def _setDataDoProcess(self, data, toset=None):
        """Process data before write.

        Returns a copy, without the fields that are not stored."""
        if toset is None:
            toset = set(data)

        # resolve dependencies
        # XXX only first order dependencies are ensured. Others depend on
        # impredictable ordering of iteration
        for ancestor, dependents in self._write_dependencies.items():
            if ancestor in toset:
                toset.update(dependents)
        # being dependent on 'all' means in particular upon fields of other
        # schemas. We have no choice but to always update.
        toset.update(self._all_dependents)

        new_data = {}
        for field_id, field in self.getFieldItems():
            if not field_id in toset:
                continue
            value = data[field_id]
            result = field.processValueBeforeWrite(value, data,
                                                   self.getContextObject(),
                                                   self.getProxy())
            if not field.write_ignore_storage:
                new_data[field_id] = result
        return new_data

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        raise NotImplementedError


class AttributeStorageAdapter(BaseStorageAdapter):
    """Attribute Storage Adapter

    This adapter simply gets and sets data from/to an attribute.
    """

    def __init__(self, schema, ob, proxy=None, **kw):
        """Create an Attribute Storage Adapter for a schema.

        The object passed is the one on which to get/set attributes.
        """
        self._ob = ob
        self._proxy = proxy
        BaseStorageAdapter.__init__(self, schema, **kw)

    def getContextObject(self):
        """Get the underlying context for this adapter."""
        return self._ob

    def setContextObject(self, context, proxy=None):
        """Set a new underlying context for this adapter."""
        self._ob = context
        self._proxy = proxy

    def getProxy(self):
        """Get the potentially associated proxy for this adapter."""
        return self._proxy

    def _getFieldData(self, field_id, field):
        """Get data from one field."""
        ob = self._ob
        if not hasattr(aq_base(ob), field_id):
            # Use default from field.
            return DEFAULT_VALUE_MARKER
        if isinstance(field, CPSSubObjectsField):
            return field.getFromAttribute(ob, field_id)
        else:
            return getattr(ob, field_id)

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        # No kw arguments are expected.
        ob = self._ob
        field = self._schema[field_id] # XXX should be an arg
        if isinstance(field, CPSSubObjectsField):
            field.setAsAttribute(ob, field_id, value)
        else:
            ob_base = aq_base(ob)

            # If the field is stored as a subobject first delete it.
            if hasattr(ob_base,'objectIds') and field_id in ob.objectIds():
                ob._delObject(field_id)

            # If it is an OFS object, store as subobject and not attribute
            if (hasattr(aq_base(value), 'manage_beforeDelete') and
                hasattr(ob_base, '_setObject')):
                if hasattr(ob_base, field_id):
                    delattr(ob, field_id)
                ob._setObject(field_id, value)
            else:
                setattr(ob, field_id, value)

    def _getContentUrl(self, object, field_id, file_name):
        deprecate_getContentUrl()
        return '%s/downloadFile/%s/%s' % (
            object.absolute_url(), field_id, file_name)

    def _getSubContentUri(self, field_id, field, absolute=False):
        """See docstring in BaseStorageAdapter."""

        proxy = self._proxy
        base = proxy is not None and proxy or self._ob
        if base is None:
            return

        fobj = self._getFieldData(field_id, field)
        if fobj is DEFAULT_VALUE_MARKER or fobj is None:
            return

        base_uri = absolute and base.absolute_url() or base.absolute_url_path()
        if base is proxy:
            return '%s/downloadFile/%s/%s' % (base_uri, field_id,
                                              urllib.quote(fobj.title_or_id()))

        return '%s/%s' % (base_uri, field_id)



ACCESSOR = object()
ACCESSOR_READ_ONLY = object()

class MetaDataStorageAdapter(BaseStorageAdapter):
    """MetaData Storage Adapter

    This adapter simply gets and sets metadata using X() and setX() methods for
    standard CMF Dublin Core methods, or using specific attributes otherwise.
    """

    _field_attributes = {
        'Creator': ACCESSOR_READ_ONLY,
        'CreationDate': ('creation_date', None),
        'Title': ACCESSOR,
        'Subject': ACCESSOR,
        'Description': ACCESSOR,
        'Contributors': ACCESSOR,
        'ModificationDate': ('modification_date', 'setModificationDate'),
        'EffectiveDate': ('effective_date', 'setEffectiveDate'),
        'ExpirationDate': ('expiration_date', 'setExpirationDate'),
        'Format': ACCESSOR,
        'Language': ACCESSOR,
        'Rights': ACCESSOR,
        'Coverage': ACCESSOR,
        'Source': ACCESSOR,
        'Relation': ACCESSOR,
        }

    def __init__(self, schema, ob, proxy=None, **kw):
        self._ob = ob
        self._proxy = proxy
        BaseStorageAdapter.__init__(self, schema, **kw)

    def getContextObject(self):
        """Get the underlying context for this adapter."""
        return self._ob

    def setContextObject(self, context, proxy=None):
        """Set a new underlying context for this adapter."""
        self._ob = context
        self._proxy = proxy

    def getProxy(self):
        """Get the potentially associated proxy for this adapter."""
        return self._proxy

    def _getFieldData(self, field_id, field):
        """Get data from one field.

        Calls the getter method.
        """
        ob = self._ob
        if ob is None:
            # Creation
            return DEFAULT_VALUE_MARKER
        attr = self._field_attributes.get(field_id, field_id)
        if attr is ACCESSOR or attr is ACCESSOR_READ_ONLY:
            return getattr(ob, field_id)()
        elif isinstance(attr, tuple):
            return getattr(ob, attr[0])
        elif hasattr(aq_base(ob), attr):
            return getattr(ob, attr)
        else:
            # Use default from field.
            return DEFAULT_VALUE_MARKER

    def _setFieldData(self, field_id, value):
        """Set data for one field.

        Calls the setter method.
        """
        # No kw arguments are expected.
        ob = self._ob
        attr = self._field_attributes.get(field_id, field_id)
        if attr is ACCESSOR:
            getattr(ob, 'set' + field_id)(value)
        elif attr is ACCESSOR_READ_ONLY:
            raise ValueError("Field %s is read-only" % field_id)
        elif isinstance(attr, tuple):
            if attr[1] is None:
                raise ValueError("Field %s is read-only" % field_id)
            getattr(ob, attr[1])(value)
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

    def getContextObject(self):
        """Get the underlying context for this adapter."""
        return self._ob

    def setContextObject(self, context, proxy=None):
        """Set a new underlying context for this adapter."""
        pass

    def _getFieldData(self, field_id, field):
        """Get data from one field."""
        return self._ob.get(field_id, DEFAULT_VALUE_MARKER)

    def _setFieldData(self, field_id, value):
        """Set data for one field."""
        # No kw arguments are expected.
        self._ob.update({field_id : value})
