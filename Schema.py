# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Authors: Florent Guillaume <fg@nuxeo.com>
#          Lennart Regebro <lr@nuxeo.com>
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
"""Schema

A Schema stores a set of fields defining the data stored in an object.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Persistence import Persistent

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties

from Products.CPSDocument.OrderedDictionary import OrderedDictionary
from Products.CPSDocument.AttributeStorageAdapter import AttributeStorageAdapterFactory

from Products.CPSDocument.Field import FieldRegistry


class OLDSchema(OrderedDictionary):
    """Defines fields used in a document"""

    # It doesn't really have to be ordered, I think a pure
    # PersistentMapping would work. But then again, it can't hurt...

    def __init__(self, adapter=None):
        OrderedDictionary.__init__(self)
        self._namespace = ''
        if not adapter:
            adapter = AttributeStorageAdapterFactory()
        self._adapter = adapter

    def setStorageAdapterFactory(self, adapter):
        self._adapter = adapter

    def getStorageAdapterFactory(self):
        return self._adapter

    def makeStorageAdapter(self, document):
        return self._adapter.makeStorageAdapter(document, \
                                 self.getFieldDictionary(), self._namespace)

    def setNamespace(self, namespace):
        self._namespace = namespace

    def getNamespace(self):
        return self._namespace

    def getFieldStorageId(self, fieldid):
        if self._namespace:
            ns = self._namespace + '_'
        else:
            ns = ''
        return ns + self[fieldid].getStorageId()

    def getFieldDictionary(self):
        """Returns all the fields as a dictionary"""
        return self.data

######################################################################
######################################################################
######################################################################

class Schema(Folder):
    """Schema

    Base class for schemas, that contain fields.
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self):
        self._clear()
        # XXX

    def _clear(self):
        """Clear the schema."""
        pass

    # Dict-like access.

    def keys(self):
        """Get the field ids."""
        return self.objectIds()

    def __getitem__(self, key):
        """Get a field."""
        try:
            return self._getOb(key)
        except AttributeError:
            raise KeyError, key

class CPSSchema(Schema):
    """Persistent Schema."""

    meta_type = "CPS Schema"

    security = ClassSecurityInfo()

    def __init__(self, id, title='', schema=None, **kw):
        self.id = id
        self.title = title
        #if schema is None:
        #    schema = Schema()
        #self.setSchema(schema)

    security.declarePrivate('addField')
    def addField(self, id, field):
        """Add a field."""
        self._setObject(id, field)
        return self._getOb(id)


    #
    # ZMI
    #

    _properties = (
        {'id': 'xxx', 'type': 'string', 'mode': 'w',
         'label':'yyy'},
        )

    manage_options = (
        {'label': 'Schema',
         'action': 'manage_editSchema',
         },
        ) + Folder.manage_options[1:]

    security.declareProtected(ManagePortal, 'manage_editSchema')
    manage_editSchema = DTMLFile('zmi/schema_editform', globals())

    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = manage_editSchema

    security.declareProtected(ManagePortal, 'manage_addField')
    def manage_addField(self, id, field_type, REQUEST):
        """Add a field TTW."""
        kw = REQUEST.form
        del kw['id']
        del kw['field_type']
        field = FieldRegistry.makeField(field_type, id, **kw)
        field = self.addField(id, field)
        REQUEST.RESPONSE.redirect(field.absolute_url()+'/manage_workspace'
                                  '?manage_tabs_message=Added.')

    security.declareProtected(ManagePortal, 'manage_delFieldItems')
    def manage_delFieldItems(self, ids, REQUEST=None):
        """Add a field TTW."""
        self.manage_delObjects(ids)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_editSchema'
                                      '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'listFieldTypes')
    def listFieldTypes(self):
        """List all field types."""
        return FieldRegistry.listFieldTypes()


InitializeClass(CPSSchema)


addCPSSchemaForm = DTMLFile('zmi/schema_addform', globals())

def addCPSSchema(container, id, REQUEST=None):
    """Add a CPS Schema."""
    ob = CPSSchema(id)
    container._setObject(id, ob)
    ob = container._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(ob.absolute_url() + "/manage_main")

