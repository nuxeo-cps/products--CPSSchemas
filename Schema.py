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

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.CPSSchemas.FolderWithPrefixedIds import FolderWithPrefixedIds
from Products.CPSSchemas.Field import FieldRegistry


class SchemaContainer(Folder):
    """Schema Container

    Stores the definition of schemas.
    """

    meta_type = 'CPS Schema Container'

    security = ClassSecurityInfo()

    def __init__(self, id):
        self._setId(id)

    security.declarePrivate('addSchema')
    def addSchema(self, id, schema):
        """Add a schema."""
        self._setObject(id, schema)
        return self._getOb(id)

    #
    # ZMI
    #

    def all_meta_types(self):
        return ({'name': 'CPS Schema',
                 'action': 'manage_addCPSSchemaForm',
                 'permission': ManagePortal},
                )

    security.declareProtected(ManagePortal, 'manage_addCPSSchemaForm')
    manage_addCPSSchemaForm = DTMLFile('zmi/schema_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSSchema')
    def manage_addCPSSchema(self, id, REQUEST=None):
        """Add a schema, called from the ZMI."""
        schema = CPSSchema(id)
        schema = self.addSchema(id, schema)
        if REQUEST:
            REQUEST.RESPONSE.redirect(schema.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Added.')
        else:
            return schema

InitializeClass(SchemaContainer)


# XXX: this class (at least, its two methods) is useless. This
# should be refactored.
class Schema(FolderWithPrefixedIds):
    """Schema

    Base class for schemas, that contain fields.
    """

    prefix = 'f__'

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    id = None

    def __init__(self, id='', title=''):
        raise "XXX: Should not be called"
        print "Schema.__init__() called (I thought it would not be)"
        self.id = id
        self.title = title
        self._clear()
        # XXX

    def _clear(self):
        raise "XXX: Should not be called"
        """Clear the schema."""
        print "Schema.clear() called (I thought it would not be)"
        pass

InitializeClass(Schema)


class CPSSchema(Schema):
    # XXX: the Schema class is already persistent.
    """Persistent Schema."""

    meta_type = "CPS Schema"

    security = ClassSecurityInfo()

    def __init__(self, id, title='', schema=None, **kw):
        self.id = id
        self.title = title
        # XXX: can we remove this + the schema and **kw parameters ?
        #if schema is None:
        #    schema = Schema()
        #self.setSchema(schema)

    security.declarePrivate('addField')
    def addField(self, id, field_type, **kw):
        """Add a new field instance."""
        field = FieldRegistry.makeField(field_type, id, **kw)
        return self.addSubObject(field)

    #
    # ZMI
    #
    _properties = (
        )

    manage_options = (
        {'label': 'Schema', 'action': 'manage_editSchema', },
        ) + FolderWithPrefixedIds.manage_options[1:] + (
        {'label': 'Export', 'action': 'manage_export', },
        )

    security.declareProtected(ManagePortal, 'manage_editSchema')
    manage_editSchema = DTMLFile('zmi/schema_editform', globals())

    security.declareProtected(ManagePortal, 'manage_export')
    manage_export = DTMLFile('zmi/schema_export', globals())

    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = manage_editSchema

    security.declareProtected(ManagePortal, 'manage_addField')
    def manage_addField(self, id, field_type, REQUEST=None, **kw):
        """Add a field TTW."""
        if REQUEST:
            kw.update(REQUEST.form)
            for key in ('id', 'field_type'):
                if kw.has_key(key):
                    del kw[key]
        field = self.addField(id, field_type, **kw)
        if REQUEST:
            REQUEST.RESPONSE.redirect(field.absolute_url()+'/manage_workspace'
                                      '?manage_tabs_message=Added.')
        else:
            return field

    security.declareProtected(ManagePortal, 'manage_delFieldItems')
    def manage_delFieldItems(self, ids, REQUEST=None):
        """Add a field TTW."""
        self.manage_delObjects(ids)
        if REQUEST:
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
    if REQUEST:
        REQUEST.RESPONSE.redirect(ob.absolute_url() + "/manage_main")
