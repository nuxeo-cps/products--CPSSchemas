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
"""Widgets Tool

The Widgets Tool manages the available widget types.
"""

from zLOG import LOG, DEBUG
from types import DictType
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import rolesForPermissionOn
from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import UniqueObject, getToolByName


class WidgetsTool(UniqueObject, Folder):
    """Widgets Tool

    Stores the available widget types.
    """

    id = 'portal_widgets'
    meta_type = 'CPS Widgets Tool'

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
        """Add a widget type, called from the ZMI."""
        wt = self.getUnstrippedWidgetType(swt)
        widget = WidgetTypeRegistry.makeWidget(wt, id)
        widget = self._setObject(widget.getId(), widget)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_workspace')

InitializeClass(WidgetsTool)


class WidgetTypeRegistry:
    """Registry of the available widget types.

    This stores python classes for widget types, and python classes for
    widgets.

    Not to be confused with the administrator-visible widget types
    stored in portal_widgets that are actually instances of those
    registered here.
    """

    def __init__(self):
        self._widget_types = []
        self._widget_type_classes = {}
        self._widget_classes = {}

    def register(self, mcls, cls):
        """Register a class for a widget type."""
        widget_type = mcls.meta_type
        self._widget_types.append(widget_type)
        self._widget_type_classes[widget_type] = mcls
        self._widget_classes[widget_type] = cls

    def listWidgetTypes(self):
        """Return the list of widget types."""
        return self._widget_types[:]

    def makeWidget(self, widget_type, id, **kw):
        """Factory to make a widget of the given type."""
        return self._widget_type_classes[widget_type](id, **kw)

    def getClass(self, widget_type):
        """Get the instance class for a widget of the given type."""
        return self._widget_classes[widget_type]

# Singleton
WidgetTypeRegistry = WidgetTypeRegistry()
