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
"""Schemas Tool
"""

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner, aq_base
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.CPSDocument.Schema import CPSSchema

_marker = []

class SchemasTool(UniqueObject, Folder):
    """Schemas Tool

    The Schemas Tool stores the definition of standard schemas. A schema
    describes a set of fields that can store data.
    """

    id = 'portal_schemas'
    meta_type = 'CPS Schemas Tool'

    security = ClassSecurityInfo()

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
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(schema.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Added.')




InitializeClass(SchemasTool)
