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
"""Layouts Tool

The Layouts Tool manages layouts.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Layout import LayoutContainer
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter


class LayoutsTool(UniqueObject, LayoutContainer):
    """Layouts Tool

    Stores persistent layout objects.
    """

    id = 'portal_layouts'
    meta_type = 'CPS Layouts Tool'

    security = ClassSecurityInfo()

    def __init__(self):
        LayoutContainer.__init__(self, self.id)

    security.declareProtected(View, 'renderLayout')
    def renderLayout(self, layout_id, schema_id, context, mapping=None,
                     layout_mode='edit', **kw):
        """Render a layout/schema.

        Return rendered, msg, ds
        rendered is the html rendering

        if mapping is not none then the layout is validate
        and msg is either 'valid' or 'invalid',

        you can add kw like style_prefix."""
        msg = ''
        stool = getToolByName(self, 'portal_schemas')
        ltool = getToolByName(self, 'portal_layouts')
        schema = stool._getOb(schema_id)
        layout = ltool._getOb(layout_id)
        adapters = [AttributeStorageAdapter(schema, None)]
        dm = DataModel(None, adapters, proxy=context, context=context)
        dm._fetch()
        dm._check_acls = 0 # this is needed to shortcut directory acl
        ds = DataStructure(datamodel=dm)
        layout.prepareLayoutWidgets(datastructure=ds)

        if mapping:
            ds.updateFromMapping(mapping)
        dm = ds.getDataModel()
        layout_structure = layout.computeLayoutStructure(
            layout_mode=layout_mode,
            datamodel=dm)
        layout = layout_structure['layout']
        if mapping:
            if layout.validateLayoutStructure(layout_structure,
                                              ds, layout_mode=layout_mode):
                msg = 'valid'
            else:
                msg = 'invalid'

        layout.renderLayoutStructure(layout_structure, ds,
                                     layout_mode=layout_mode)

        rendered = layout.renderLayoutStyle(layout_structure,
                                            ds, context,
                                            first_layout=0,
                                            last_layout=0,
                                            is_flexible=0,
                                            layout_mode=layout_mode,
                                            **kw)
        return rendered, msg, ds


InitializeClass(LayoutsTool)
