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
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.CPSDocument.Layout import CPSLayout


class LayoutsTool(UniqueObject, Folder):
    """Layouts Tool

    Stores persistent layout objects.
    """

    id = 'portal_layouts'
    meta_type = 'CPS Layouts Tool'

    security = ClassSecurityInfo()

    security.declarePrivate('addLayout')
    def addLayout(self, id, layout):
        """Add a layout."""
        self._setObject(id, layout)
        return self._getOb(id)

    #
    # ZMI
    #

    def all_meta_types(self):
        return ({'name': 'CPS Layout',
                 'action': 'manage_addCPSLayoutForm',
                 'permission': ManagePortal},
                )


    security.declareProtected(ViewManagementScreens, 'manage_addCPSLayoutForm')
    manage_addCPSLayoutForm = DTMLFile('zmi/layout_addform', globals())

    security.declareProtected(ManagePortal, 'manage_addCPSLayout')
    def manage_addCPSLayout(self, id, REQUEST):
        """Add a layout, called from the ZMI."""
        layout = CPSLayout(id)
        layout = self.addLayout(id, layout)
        REQUEST.RESPONSE.redirect(layout.absolute_url()+'/manage_main'
                                  '?psm=Added.')


InitializeClass(LayoutsTool)


