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
"""Widget Types Tool

The Widget Types Tool manages the available widget types.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import UniqueObject


class WidgetTypesTool(UniqueObject, Folder):
    """Widget Types Tool

    Stores the available widget types.
    """

    id = 'portal_widget_types'
    meta_type = 'CPS Widget Types Tool'

    security = ClassSecurityInfo()

    #
    # ZMI
    #
    def all_meta_types(self):
        return [
            {'name': wt,
             'action': 'manage_addCPSWidgetTypeForm/' + wt.replace(' ', ''),
             'permission': ManagePortal}
            for wt in WidgetTypeRegistry.listWidgetTypes()]


    security.declareProtected(ManagePortal, 'manage_addCPSWidgetTypeForm')
    manage_addCPSWidgetTypeForm = DTMLFile('zmi/widgettype_addform', globals())

    security.declareProtected(ManagePortal, 'getUnstrippedWidgetType')
    def getUnstrippedWidgetType(self, widget_type):
        """Get an unstripped version of a widget type name."""
        swt = widget_type.replace(' ', '')
        for wt in WidgetTypeRegistry.listWidgetTypes():
            if wt.replace(' ', '') == swt:
                return wt
        raise ValueError(widget_type)

    security.declareProtected(ManagePortal, 'manage_addCPSWidgetType')
    def manage_addCPSWidgetType(self, id, swt, REQUEST=None):
        """Add a widget type instance."""
        wt = self.getUnstrippedWidgetType(swt)
        widget_type_instance = WidgetTypeRegistry.makeWidgetTypeInstance(wt, id)
        self._setObject(widget_type_instance.getId(), widget_type_instance)
        widget_type_instance = self._getOb(widget_type_instance.getId())
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_workspace')
        else:
            return widget_type_instance

InitializeClass(WidgetTypesTool)


class WidgetTypeRegistry:
    """Registry of the available widget types.

    This stores python classes for widget types, and python classes for
    widgets.

    Not to be confused with the administrator-visible widget types
    stored in portal_widget_types that are actually instances of those
    registered here.
    """

    def __init__(self):
        self._widget_types = []
        self._widget_type_classes = {}
        self._widget_classes = {}

    def register(self, mcls, cls=None):
        """Register a class for a widget type."""
        widget_type = mcls.meta_type
        self._widget_types.append(widget_type)
        self._widget_type_classes[widget_type] = mcls
        if not cls:
            cls = mcls.cls
        self._widget_classes[widget_type] = cls

    def listWidgetTypes(self):
        """Return the list of widget types."""
        return self._widget_types[:]

    def makeWidgetTypeInstance(self, widget_type, id, **kw):
        """Factory to make a widget type instance of the given type
        with id = <id>."""
        return self._widget_type_classes[widget_type](id, **kw)

    def getClass(self, widget_type):
        """Get the instance class for a widget of the given type."""
        return self._widget_classes[widget_type]

# Singleton
WidgetTypeRegistry = WidgetTypeRegistry()
