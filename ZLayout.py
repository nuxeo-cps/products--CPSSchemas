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
"""ZLayout

Persistent layout for Flexible Type Information.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties


class ZLayout(SimpleItemWithProperties):
    """Persistent Layout."""

    meta_type = "CPS Layout"


class LayoutContainer(Folder):
    """Container for Layouts.

    Restricts the available creatable subtypes.
    """

    meta_type = "CPS Layout Container"

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = (
        {'name': ZLayout.meta_type,
         'action':'addLayout',
         },
        )

    def __init__(self, id):
        self.id = id

    def addLayout(self, id, REQUEST=None):
        """Add a Layout."""
        layout = ZLayout(id)
        self._setObject(id, layout)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() +
                                      "?manage_tabs_message=Added.")

InitializeClass(LayoutContainer)
