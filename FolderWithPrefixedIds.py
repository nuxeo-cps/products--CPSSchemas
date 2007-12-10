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
"""
Folder whose subobjects' ids are automatically prefixed, so that
they can be arbitrary.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.CMFCore.permissions import AccessContentsInformation


class FolderWithPrefixedIds(Folder):
    """Folder with prefixed ids.

    All subobjects' ids are prefixed, so that they can be arbitrary.
    """

    prefix = 'prefix__'

    security = ClassSecurityInfo()

    security.declarePrivate('addSubObject')
    def addSubObject(self, ob):
        """Add a subobject, with a correctly prefixed id.

        Returns the subobject in its acquisition chain.
        """
        id = ob.getId().strip()
        if not id.startswith(self.prefix):
            id = self.prefix + id
            ob._setId(id)
        self._setObject(id, ob)
        return self._getOb(id)

    security.declarePrivate('delSubObject')
    def delSubObject(self, id):
        """Delete a subobject, with a correctly prefixed id."""
        if not id.startswith(self.prefix):
            id = self.prefix + id
        self._delObject(id)

    security.declarePublic('getIdUnprefixed')
    def getIdUnprefixed(self, id):
        """ """
        if id.startswith(self.prefix):
            return id[len(self.prefix):]
        else:
            return id

    # Simple dict-like access without prefix

    def __getitem__(self, key):
        """Dictionary-like access without prefix."""
        prefix = self.prefix
        if not key.startswith(prefix):
            key = prefix + key
        try:
            return self._getOb(key)
        except AttributeError:
            raise KeyError(key)

    security.declareProtected(AccessContentsInformation, 'keys')
    def keys(self):
        """Return subobjects ids without prefix."""
        keys = []
        prefix = self.prefix
        prefixlen = len(prefix)
        for id in self.objectIds():
            if id.startswith(prefix):
                keys.append(id[prefixlen:])
        return keys

    security.declareProtected(AccessContentsInformation, 'items')
    def items(self):
        """Return items, ids without prefix."""
        items = []
        prefix = self.prefix
        prefixlen = len(prefix)
        for id, value in self.objectItems():
            if id.startswith(prefix):
                items.append((id[prefixlen:], value))
        return items

    security.declareProtected(AccessContentsInformation, 'has_key')
    def has_key(self, key):
        """Test if key is present."""
        if not key.startswith(self.prefix):
            key = self.prefix + key
        return key in self.objectIds()

InitializeClass(FolderWithPrefixedIds)
