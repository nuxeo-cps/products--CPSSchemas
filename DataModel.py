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

The storage itself is done through a storage adapter.
"""

import logging

from Acquisition import aq_base
from UserDict import UserDict
from cgi import escape

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl import getSecurityManager
from OFS.Image import File

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent

logger = logging.getLogger('Products.CPSSchemas.DataModel')

try:
    True
except NameError:
    True = 1
    False = 0

class DefaultValue:
    def __str__(self):
        return "<DefaultValue for field>"

DEFAULT_VALUE_MARKER = DefaultValue()


class AccessError(ValueError):
    """Raised by a field when access is denied."""

    def __init__(self, field, message=''):
        self.field = field
        self.message = message

    def __str__(self):
        s = "%s access to %s denied" % (self.type, self.field)
        if self.message:
            s += " ("+self.message+") "
        return s

class ReadAccessError(AccessError):
    type = "Read"

class WriteAccessError(AccessError):
    type = "Write"

class ValidationError(ValueError):
    """Raised by a widget or a field when user input is incorrect."""
    pass


def is_file_object(obj):
    """Tell if given obj is a file object.
    Making this a function gives room for enhancement (PERF)
    and unit tests monkey patching."""
    return isinstance(obj, File)

_marker = object()

class ProtectedFile(object):
    def __init__(self, file_obj, datamodel, dm_key):
        # avoid loop
        object.__setattr__(self, '_datamodel', datamodel)
        self._file_obj = file_obj
        self._dm_key = dm_key

    def setFile(self, fobj):
        """change the referenced file object."""
        object.__setattr__(self, '_file_obj', fobj)

    def __getattr__(self, attr, default=_marker):
        if default is _marker:
            return getattr(self._file_obj, attr)
        return getattr(self._file_obj, attr, default)

    def __setattr__(self, attr, v):
        if not attr.startswith('_'):
            self._datamodel.dirty.add(self._dm_key)
        object.__setattr__(self, attr, v)

class DataModel(UserDict):
    """An abstraction for the data stored in an object."""

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, ob, adapters=(), proxy=None, context=None,
                 add_roles=()):
        """Constructor.

        Proxy must be passed, if different than the object, so that
        an editable content can be created at commit time.

        Context must be passed if the widgets or fields have some
        placeful computations to do. Be careful that the context may not
        be the proxy but its container during creation.

        The context is also the one used for acl checks.
        """
        UserDict.__init__(self)
        # self.data initialized by UserDict
        self._ob = ob
        self._adapters = adapters
        self._proxy = proxy

        # This set keeps track of field ids whose data is "dirty"
        # (has been modified).
        self.dirty = set()

        if context is None:
            if proxy is not None:
                context = proxy
            else:
                context = ob
        self._context = context
        fields = {}
        schemas = []
        for adapter in adapters:
            schema = adapter.getSchema()
            for fieldid, field in schema.items():
                if fields.has_key(fieldid):
                    sids = [a._schema.getId() for a in adapters
                            if fieldid in a._schema.keys()]
                    logger.warn(
                        "Field '%s' is in schema %s but also in schema%s %s.",
                        fieldid, sids[0], len(sids) > 2 and 's' or '',
                        ', '.join(sids[1:]))
                    continue
                fields[fieldid] = field
            schemas.append(schema)
        self._schemas = tuple(schemas)
        self._fields = fields
        # Precomputed things used for validation
        user = getSecurityManager().getUser()
        self._acl_cache_user = user
        self._setAddRoles(add_roles)
        self._check_acls = 1
        self._forbidden_widgets = []

    def _setAddRoles(self, add_roles):
        user = self._acl_cache_user
        user_roles = (tuple(user.getRolesInContext(self._context)) +
                      tuple(add_roles))
        self._acl_cache_user_roles = user_roles
        self._acl_cache_permissions = {} # dict with perm: hasit/not

    #
    # Restricted accessors
    #
    def checkReadAccess(self, key):
        if self._check_acls:
            self._fields[key].checkReadAccess(self, self._context)

    def checkWriteAccess(self, key):
        if self._check_acls:
            self._fields[key].checkWriteAccess(self, self._context)

    def __getitem__(self, key):
        self.checkReadAccess(key)
        return self.data[key]

    def get(self, key, failobj=None):
        try:
            self.checkReadAccess(key)
        except (ReadAccessError, KeyError):
            return failobj
        return self.data.get(key, failobj)

    def items(self):
        for key in self.data.keys():
            self.checkReadAccess(key)
        return self.data.items()

    def values(self):
        for key in self.data.keys():
            self.checkReadAccess(key)
        return self.data.values()

    def popitem(self):
        key, item = self.data.popitem()
        self.checkReadAccess(key)
        return key, item

    def pop(self, key, *args):
        # python2.3
        self.checkReadAccess(key)
        return self.data.pop(key, *args)

    def __setitem__(self, key, item):
        self.checkWriteAccess(key)
        self.data[key] = item
        self.dirty.add(key)

    def isDirty(self, key):
        """Is the item marked dirty ?"""
        return key in self.dirty

    # Expose setter as method for restricted code.
    def set(self, key, item):
        self.checkWriteAccess(key)
        self[key] = item

    def update(self, dict):
        for key in dict.keys():
            self.checkWriteAccess(key)
        UserDict.update(self, dict)

    def setdefault(self, key, failobj=None):
        self.checkReadAccess(key)
        self.checkWriteAccess(key)
        return UserDict.setdefault(self, key, failobj=failobj)

    # Unrestricted accessors

    def _itemsWithFields(self):
        """Get a sequence of (key, value, field) from the current data.

        Keys are sorted.
        """
        data = self.data
        fields = self._fields
        keys = data.keys()
        keys.sort()
        res = [(key, data[key], fields[key]) for key in keys]
        return res

    # XXX python2.2 iterators not done.

    #
    # DataModel accessors
    #
    def getObject(self):
        """Get the object this DataModel is about."""
        return self._ob

    def getProxy(self):
        """Get the proxy of the object for this DataModel."""
        return self._proxy

    def getContext(self):
        """Get the context for this DataModel."""
        return self._context

    #
    # Fetch and commit
    #
    def _fetch(self):
        """Fetch the data into local dict for user access."""
        data = self.data
        fields = self._fields
        for adapter in self._adapters:
            data.update(adapter.getData())
        for field_id, value in data.items():
            if value is DEFAULT_VALUE_MARKER:
                # Default values are dirty because they have
                # to be considered changed by the user
                # (and written, and used for dependent computations)
                field = fields[field_id]
                data[field_id] = field.getDefault(self)
                self.dirty.add(field_id)
            if is_file_object(value):
                self._protectFile(field_id, value)

    def _getProtectedFileIds(self):
        """Return the current set of protected file's ids.

        Caching that is bad idea: None is a suitable value."""

        return set(field_id for field_id, value in self.data.items()
                   if isinstance(value, ProtectedFile))

    def _updateProtectedFiles(self):
        """Reload File fields and update references within protected files."""

        refetched = {}
        # GR: duplicated bit necessary. Enhancing _fetch for partial data
        # leads to side effects
        for adapter in self._adapters:
            refetched.update(adapter.getData(
                field_ids=self._getProtectedFileIds()))
        for f_id, value in refetched.items():
            self.data[f_id].setFile(value)

    def _setEditable(self):
        """Set the editable object for this DataModel.

        Uses the proxy passed to the constructor.

        Future uses of the DataModel will refer to the editable object.

        Needed by CPS because getEditableContent may have to be called
        on the proxy before the object is ready for modification (CPS
        uses this to provide "freezing", a lazy unsharing of objects).
        """
        proxy = self._proxy
        if proxy is None:
            return
        if not hasattr(aq_base(proxy), 'getEditableContent'):
            return
        ob = old_ob = self._ob
        if ob is None:
            return
        # Get the language from the doc to be sure we have the correct one.
        if hasattr(aq_base(ob), 'Language'):
            lang = ob.Language()
        else:
            lang = None
        if not lang:
            # If object is unitialized, Language comes from the datamodel.
            lang = self.get('Language')
        ob = proxy.getEditableContent(lang=lang)
        if ob is not None and ob is not old_ob:
            self._setObject(ob, proxy=proxy)
            self._updateProtectedFiles()

    def _setObject(self, ob, proxy=None):
        """Set the object (and proxy) this datamodel is about.

        Used when a datamodel is switched to a new editable content,
        or to a newly created object.
        """
        self._ob = ob
        self._proxy = proxy
        for adapter in self._adapters:
            adapter.setContextObject(ob, proxy)

    def _unProtectFiles(self):
        for f_id in self._getProtectedFileIds():
            protected = self.data[f_id]
            self.data[f_id] = fobj = protected._file_obj
            for attr, v in protected.__dict__.items():
                if attr.startswith('_'):
                    continue
                setattr(fobj, attr, v)

    def _protectFiles(self):
        for fi, fv in self.data.items():
            if isinstance(fv, File):
                self._protectFile(fi, fv)

    def _protectFile(self, field_id, value):
        self.data[field_id] = ProtectedFile(value, self, field_id)

    def _commit(self, check_perms=1, _set_editable=True):
        """Commit modified data into object.

        Returns the resulting object.

        Try to re-get an editable version of the object before modifying
        it. This is needed by CPS for frozen objects and can be bypassed
        with the _set_editable kwarg. This bypass should be used at creation
        time only: the proxy doesn't know the new object yet in this case.
        """
        if _set_editable:
            self._setEditable()
        ob = self._ob

        # Check permission on the object.
        # This is global and in addition to field-level checks.
        # XXX This should somehow be checked by the adapters.
        if (ob is not None and check_perms and
            not _checkPermission(ModifyPortalContent, ob)):
            logger.warn("Unauthorized to modify object %s", ob)
            raise Unauthorized("Cannot modify object")

        self._commitData()

        # XXX temporary until we have a better API for this
        if hasattr(aq_base(ob), 'postCommitHook'):
            ob.postCommitHook(datamodel=self)

        return ob

    def _commitData(self):
        """Compute dependent fields and write data into object."""

        # apply changes to file objects and decapsulate
        self._unProtectFiles()

        # Compute dependent fields.
        data = self.data
        for schema in self._schemas:
            for field_id, field in schema.items():
                if self.isDirty(field_id):
                    field.computeDependantFields(self._schemas, data,
                                                 context=self._context)
                    for dep_id in field._getAllDependantFieldIds():
                        self.dirty.add(dep_id)

        # Call the adapters to store the data.
        for adapter in self._adapters:
            adapter.setData(data, toset=self.dirty)

        # nothing's dirty any more
        self.dirty = set()

        # reprotect file objects for further changes
        self._protectFiles()

    #
    # Import/export
    #
    def _exportAsXML(self):
        """Export the datamodel as XML string."""
        res = []
        data = self.data
        for schema in self._schemas:
            for field_id, field in schema.items():
                value = data[field_id]
                svalue, info = field._exportValue(value)
                s = '  <field id="%s"' % escape(field_id)
                if info:
                    attrs = ['%s="%s"' % (k, escape(str(v)))
                             for k, v in info.items()]
                    s += ' ' + ' '.join(attrs)
                s += '>' + svalue + '</field>'
                res.append(s)
        return '\n'.join(res)

    def __repr__(self):
        return '<DataModel %s>' % (self.data,)

InitializeClass(DataModel)
