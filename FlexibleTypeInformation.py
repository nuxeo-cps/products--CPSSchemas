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
"""Flexible Type Information

Type information for types described by a flexible set of schemas and layout.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo, Unauthorized

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.TypesTool import TypeInformation

from Products.CPSDocument.CPSDocument import addCPSDocument
from Products.CPSDocument.DataModel import DataModel
from Products.CPSDocument.DataStructure import DataStructure


# inserted into TypesTool by PatchTypesTool
addFlexibleTypeInformationForm = DTMLFile('zmi/addflextiform', globals())

def addFlexibleTypeInformation(container, id, REQUEST=None):
    """Add a Flexible Type Information."""
    flexti = FlexibleTypeInformation(id)
    container._setObject(id, flexti)
    flexti = container._getOb(id)
    # XXX not CMF 1.4 compatible
    flexti.addAction('view',
                     'View',
                     'cpsdocument_view',
                     # XXX CMF 1.4: condition,
                     View,
                     'object')
    flexti.addAction('edit',
                     'Edit',
                     'cpsdocument_edit_form',
                     # XXX CMF 1.4: condition,
                     ModifyPortalContent,
                     'object')
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(container.absolute_url() + "/manage_main")

# XXX add this at construction above
factory_type_information = (
    {'id': 'CPS Document',
     'title': "CPS Document",
     'description': "A base CPS document.",
     'icon': 'cpsdocument_icon.gif',
     'immediate_view': 'metadata_edit_form',
     #'product': 'CPSDocument',
     #'factory': 'addCPSDocument',
     #'meta_type': 'Dummy',
     # CPS attr
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'dummy_view',
                  'permissions': (View,),
                  },
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'dummy_edit_form',
                  'permissions': (ModifyPortalContent,),
                  },
                 {'id': 'metadata',
                  'name': 'Metadata',
                  'action': 'metadata_edit_form',
                  'permissions': (ModifyPortalContent,),
                  },
                 # CPS actions
                 {'id': 'isproxytype',
                  'name': 'isproxytype',
                  'action': 'document',
                  'permissions': (None,),
                  'visible': 0,
                  },
                 )
     },
    )


class FlexibleTypeInformation(TypeInformation):
    """Flexible Type Information

    Describes how to construct a form-based document.
    Provides resources to manage them.
    """

    meta_type = 'CPS Flexible Type Information'

    security = ClassSecurityInfo()

    _properties = (
        TypeInformation._basic_properties +
        ({'id': 'permission', 'type': 'string', 'mode': 'w',
          'label': 'Constructor permission'},
         # XXX Make above menus.
         ) +
        TypeInformation._advanced_properties +
        (
         {'id': 'schemas', 'type': 'tokens', 'mode': 'w', 'label': 'Schemas'},
         {'id': 'layout', 'type': 'string', 'mode': 'w', 'label': 'Layout'},
         )
        )
    content_meta_type = 'CPS Document'
    permission = 'Add portal content'
    schemas = []
    # XXX assume fixed storage adapters for now
    layout = ''

    def __init__(self, id, **kw):
        TypeInformation.__init__(self, id, **kw)

    #
    # ZMI
    #

##     manage_options = (
##         TypeInformation.manage_options[:2] + # Properties, Actions
##         ({'label':'Schemas', 'action':'manage_schemas'},
##          {'label':'Layouts', 'action':'manage_layouts'},
##          ) +
##         TypeInformation.manage_options[2:])

##     security.declareProtected(ManagePortal, 'flexti_schemas')
##     manage_schemas = DTMLFile('zmi/flexti_schemas', globals())

##     security.declareProtected(ManagePortal, 'flexti_layouts')
##     manage_layouts = DTMLFile('zmi/flexti_layouts', globals())

    #
    # Agent methods
    #

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed(self, container):
        """Does the current user have the permission required in
        order to construct an instance in the container?
        """
        ok = _checkPermission(self.permission, container)
        LOG('FlexibleTypeInformation', DEBUG, 'isConstructionAllowed in %s: %s'
            % ('/'.join(container.getPhysicalPath()), ok))
        return ok

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type in
        'container', using 'id' as its id.

        Returns the object.
        """
        if not self.isConstructionAllowed(container):
            raise Unauthorized
        ob = addCPSDocument(container, id, **kw)
        # XXX fill-in defaults
        # XXX
        return self._finishConstruction(ob)

    #
    # Flexible behavior
    #

    security.declarePrivate('getSchemaIds')
    def getSchemaIds(self):
        """Get the schema ids for this type."""
        return self.schemas

    security.declarePrivate('getDataModel')
    def getDataModel(self, ob):
        """Get the datamodel for an object of this type."""
        stool = getToolByName(self, 'portal_schemas')
        dm = DataModel(ob)
        for schema_id in self.getSchemaIds():
            schema = stool._getOb(schema_id, None)
            if schema is None:
                LOG('FlexibleTypeInformation', ERROR,
                    'getDataModel: missing schema %s' % schema_id)
                # XXX raise exception
                continue
            dm.addSchema(schema)
        dm._fetch()
        return dm

    security.declarePrivate('getLayout')
    def getLayout(self):
        """Get the layout for this type."""
        ltool = getToolByName(self, 'portal_layouts')
        layout = ltool._getOb(self.layout, None)
        if layout is None:
            raise ValueError("No layout '%s'" % self.layout)
        return layout


    security.declarePrivate('renderObject')
    def renderObject(self, ob, mode='view'):
        """Render the object."""
        dm = self.getDataModel(ob)
        ds = DataStructure()
        layoutob = self.getLayout()
        layout = layoutob.getLayoutData(ds, dm)
        layout_style = getattr(ob, 'layout_flex_'+mode) # XXX make customizable
        rendered = layout_style(mode=mode, layout=layout, ds=ds, dm=dm)
        return rendered

    security.declarePrivate('renderEditObject')
    def renderEditObject(self, ob, REQUEST, errmode='edit', okmode='edit'):
        """Maybe modify the object from request, and redirect to new mode."""
        dm = self.getDataModel(ob)
        ds = DataStructure()
        layoutob = self.getLayout()
        layoutdata = layoutob.getLayoutData(ds, dm)
        if REQUEST.has_key('cpsdocument_edit_button'):
            ds.updateFromRequest(REQUEST)
            ok = layoutob.validateLayout(layoutdata, ds, dm)
            if ok:
                # Update the object from dm.
                dm._commit()
                mode = okmode
            else:
                mode = errmode
        else:
            ok = 1
            mode = okmode
        layout_style = getattr(ob, 'layout_flex_'+mode) # XXX make customizable
        rendered = layout_style(mode=mode, layout=layoutdata, ds=ds, dm=dm, ok=ok)
        return rendered

    security.declareProtected(View, 'getDataStructure')
    def getDataStructure(self, ob):
        """Get the datastructure for an object of this type."""
        pass



    security.declarePublic('getSchemas')
    def getSchemas(self):
        """Get the sequence of schemas describing this type.

        Returns a sequence of Schema objects.
        """
        return []

    #
    # Management
    #

    def addSchema(self, schema):
        """Add a schema."""
        pass



InitializeClass(FlexibleTypeInformation)


