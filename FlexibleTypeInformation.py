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
    else:
        return flexti

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
         {'id': 'schemas', 'type': 'tokens', 'mode': 'w',
          'label': 'Schemas'},
         {'id': 'default_layout', 'type': 'string', 'mode': 'w',
          'label': 'Default layout'},
         {'id': 'layout_style_prefix', 'type': 'string', 'mode': 'w',
          'label': 'Layout style prefix'},
         )
        )
    content_meta_type = 'CPS Document'
    permission = 'Add portal content'
    schemas = []
    # XXX assume fixed storage adapters for now
    default_layout = ''
    layout_style_prefix = ''

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
        ob = self._constructInstance(container, id, *args, **kw)
        return self._finishConstruction(ob)

    security.declarePrivate('_constructInstance')
    def _constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type.

        Does not do CMF-specific checks or workflow insertions.

        Returns the object.
        """
        ob = addCPSDocument(container, id, **kw)
        # XXX fill-in defaults
        # XXX
        return ob

    #
    # Flexible behavior
    #

    security.declarePrivate('getSchemas')
    def getSchemas(self):
        """Get the schemas for our type.

        Returns a sequence of Schema objects.
        """
        stool = getToolByName(self, 'portal_schemas')
        schemas = []
        for schema_id in self.schemas:
            schema = stool._getOb(schema_id, None)
            if schema is None:
                raise RuntimeError("Missing schema '%s' in portal_type '%s'"
                                   % (schema_id, self.getId()))
            schemas.append(schema)
        return schemas

    security.declarePrivate('getDataModel')
    def getDataModel(self, ob):
        """Get the datamodel for an object of our type."""
        schemas = self.getSchemas()
        dm = DataModel(ob, schemas)
        dm._fetch()
        return dm

    security.declarePrivate('getLayout')
    def getLayout(self, layout_id=None):
        """Get the layout for our type."""
        ltool = getToolByName(self, 'portal_layouts')
        if not layout_id:
            layout_id = self.default_layout
        layout = ltool._getOb(layout_id, None)
        if layout is None:
            raise ValueError("No layout '%s'" % layout_id)
        return layout

    security.declarePrivate('_renderLayoutStyle')
    def _renderLayoutStyle(self, ob, mode, **kw):
        layout_meth = self.layout_style_prefix + mode
        layout_style = getattr(ob, layout_meth, None)
        if layout_style is None:
            raise RuntimeError("No layout method '%s'" % layout_meth)
        return layout_style(mode=mode, **kw)

    security.declarePrivate('renderObject')
    def renderObject(self, ob, mode='view', layout_id=None):
        """Render the object."""
        dm = self.getDataModel(ob)
        ds = DataStructure()
        layoutob = self.getLayout(layout_id)
        layout = layoutob.getLayoutData(ds, dm)
        return self._renderLayoutStyle(ob, mode, layout=layout,
                                       datastructure=ds, datamodel=dm)

    security.declarePrivate('renderEditObject')
    def renderEditObject(self, ob, request=None, layout_id=None,
                         errmode='edit', okmode='edit'):
        """Maybe modify the object from request, and renders to new mode."""
        dm = self.getDataModel(ob)
        ds = DataStructure()
        layoutob = self.getLayout(layout_id)
        layoutdata = layoutob.getLayoutData(ds, dm)
        if (request is not None
            and request.has_key('cpsdocument_edit_button')): # XXX customizable
            ds.updateFromMapping(request.form)
            ok = layoutob.validateLayout(layoutdata, ds, dm)
            if ok:
                # Update the object from dm.
                dm._commit()
                mode = okmode
                # CMF/CPS stuff.
                ob.reindexObject()
                evtool = getToolByName(self, 'portal_eventservice', None)
                if evtool is not None:
                    evtool.notify('sys_modify_object', ob, {})
            else:
                mode = errmode
        else:
            ok = 1
            mode = okmode
        return self._renderLayoutStyle(ob, mode, layout=layoutdata,
                                       datastructure=ds, datamodel=dm, ok=ok)

    security.declarePrivate('editObject')
    def editObject(self, ob, mapping):
        """Modify the object's fields from a mapping."""
        dm = self.getDataModel(ob)
        for key, value in mapping.items():
            if dm.has_key(key):
                dm[key] = value
        dm._commit()
        # CMF/CPS stuff.
        ob.reindexObject()
        evtool = getToolByName(self, 'portal_eventservice', None)
        if evtool is not None:
            evtool.notify('sys_modify_object', ob, {})

InitializeClass(FlexibleTypeInformation)


