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
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder, manage_addFolder
from Products.CMFCore.TypesTool import TypeInformation

from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.CPSDocument.ZLayout import LayoutContainer
from Products.CPSDocument.ZSchema import SchemaContainer


# inserted into TypesTool by PatchTypesTool
addFlexibleTypeInformationForm = DTMLFile('zmi/addflextiform', globals())

def addFlexibleTypeInformation(container, id, REQUEST=None):
    """Add a Flexible Type Information."""
    flexti = FlexibleTypeInformation(id)
    container._setObject(id, flexti)
    flexti = container._getOb(id)
    # Add standard containers.
    ob = LayoutContainer('layouts')
    flexti._setObject(ob.id, ob)
    ob = SchemaContainer('schemas')
    flexti._setObject(ob.id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(container.absolute_url() + "/manage_main")


class FlexibleTypeInformation(TypeInformation, Folder):
    """Flexible Type Information

    Describes how to construct a form-based document.
    Provides resources to manage them.
    """

    meta_type = 'CPS Flexible Type Information'

    security = ClassSecurityInfo()

    _properties = (
        TypeInformation._basic_properties +
##         ({'id':'permission', 'type': 'string', 'mode':'w',
##           'label':'Constructor permission'},
##          {'id':'constructor_path', 'type': 'string', 'mode':'w',
##           'label':'Constructor path'},
##          ) +
        TypeInformation._advanced_properties)

    def __init__(self, id, **kw):
        TypeInformation.__init__(self, id, **kw)

    #
    # ZMI
    #

    manage_options = (
        TypeInformation.manage_options[:2] + # Properties, Actions
        ({'label':'Schemas', 'action':'schemas/manage_main'},
         {'label':'Layouts', 'action':'layouts/manage_main'},
         ) +
        TypeInformation.manage_options[2:])

    #
    # Agent methods
    #

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed(self, container):
        """Does the current user have the permission required in
        order to construct an instance in the container?
        """

        pass

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type in
        'container', using 'id' as its id.

        Returns the object.
        """


        return self._finishConstruction(ob)

    #
    # Specific behavior
    #

    security.declarePublic('getSchemas')
    def getSchemas(self):
        """Get the sequence of schemas describing this type.

        Returns a sequence of Schema objects.
        """
        return []

    security.declarePublic('getLayout')
    def getLayout(self, viewname):
        """Get the layout for a given view.

        Returns a Layout object.
        """
        raise NotImplementedError

    #
    # Management
    #

    def addSchema(self, schema):
        """Add a schema."""
        pass



InitializeClass(FlexibleTypeInformation)


