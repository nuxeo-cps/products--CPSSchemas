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
"""Layout Tool

A layout tool manages layouts.
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


class LayoutTool(UniqueObject, Folder):
    """Layout Tool

    Stores persistent layout objects.
    """

    id = 'portal_layouts'
    meta_type = 'CPS Layout Tool'

    security = ClassSecurityInfo()

    #
    # ZMI
    #

    manage_options = (
        {'label': 'Layouts',
         'action': 'manage_listLayouts',
         },
        ) + Folder.manage_options[1:]

    security.declareProtected(ViewManagementScreens, 'manage_listTrees')
    manage_listLayouts = DTMLFile('zmi/trees_content', globals())

    security.declareProtected(ViewManagementScreens, 'manage_addCPSTreeCacheForm')
    manage_addCPSTreeCacheForm = DTMLFile('zmi/tree_add', globals())


InitializeClass(LayoutTool)


