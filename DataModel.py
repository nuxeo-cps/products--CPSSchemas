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
from cgi import escape

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent

from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter


class ValidationError(Exception):
    """Validation error during field storage."""
    pass


class DataModel(UserDict):
    """An abstraction for the data stored in an object.
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, ob, adapters=(), proxy=None, context=None):
        """Constructor.

        Proxy must be passed, if different than the object, so that
        an editable content can be created at commit time.

        Context must be passed if the widgets or fields have some
        placeful computations to do. Be careful that the context may not
        be the proxy but its container during creation.
        """
        UserDict.__init__(self)
        # self.data initialized by UserDict
        self._ob = ob
        self._adapters = adapters
        self._proxy = proxy
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
                    raise KeyError("Two schemas have field id %s "
                                   " but field ids must be unique" % fieldid)
                fields[fieldid] = field
            schemas.append(schema)
        self._schemas = tuple(schemas)
        self._fields = fields

    def getObject(self):
        """Get the object this DataModel is about."""
        # XXX used by what ???
        return self._ob

    def getProxy(self):
        """Get the proxy of the object for this DataModel."""
        return self._proxy

    def getContext(self):
        """Get the context for this DataModel."""
        return self._context

    # Expose setter as method for restricted code.
    def set(self, key, value):
        # XXX This should check field permission access...
        self.__setitem__(key, value)

    def _fetch(self):
        """Fetch the data into local dict for user access."""
        for adapter in self._adapters:
            self.data.update(adapter.getData())

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
        ob = proxy.getEditableContent(lang=lang)
        if ob is not old_ob:
            self._setObject(ob)

    def _setObject(self, ob, proxy=None):
        """Set the object (and proxy) this datamodel is about.

        Used when a datamodel is switched to a new editable content,
        or to a newly created object.
        """
        self._ob = ob
        self._proxy = proxy
        for adapter in self._adapters:
            adapter.setContextObject(ob)

    def _commit(self, check_perms=1):
        """Commit modified data into object.

        Returns the resulting object.

        Try to re-get an editable version of the object before modifying
        it. This is needed by CPS for frozen objects.
        """
        self._setEditable()
        ob = self._ob

        # Check permission on the object.
        # This is global and in addition to field-level checks.
        # XXX This should somehow be checked by the adapters.
        if (ob is not None and check_perms and
            not _checkPermission(ModifyPortalContent, ob)):
            LOG("_commit", DEBUG, "Unauthorized to modify object %s" % (ob,))
            raise Unauthorized("Cannot modify object")

        # Compute dependant fields.
        data = self.data
        for schema in self._schemas:
            for field_id, field in schema.items():
                field.computeDependantFields(self._schemas, data,
                                             context=self._context)

        # Call the adapters to store the data.
        for adapter in self._adapters:
            adapter.setData(data)

        # XXX temporary until we have a better API for this
        if hasattr(aq_base(ob), 'postCommitHook'):
            ob.postCommitHook()

        return ob

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
                    s += ' '+' '.join(attrs)
                s += '>'+svalue+'</field>'
                res.append(s)
        return '\n'.join(res)


    def __repr__(self):
        return '<DataModel %s>' % (self.data,)

InitializeClass(DataModel)
